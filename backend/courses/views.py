from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import CourseSerializer, CourseListSerializer, ChapterListSerializer
from .models import Course, Chapter
from .tasks import create_and_vectorize_course

from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI


# Create your views here.
class CourseList(APIView):
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            ser = CourseListSerializer(obj)
            create_and_vectorize_course.delay(obj.courseid, obj.title)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        limit = request.GET.get('limit', 10)
        courses = Course.objects.all()[:limit]
        serializer = CourseListSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChapterList(APIView):
     def get(self, request, courseid):
        course = Course.objects.get(courseid=courseid)
        chapter = Chapter.objects.filter(course=course)
        course_ser = CourseListSerializer(course)
        chapter_ser = ChapterListSerializer(chapter, many=True)
        return Response({"course": course_ser.data, "chapters": chapter_ser.data}, status=status.HTTP_200_OK)
    
class CourseChat(APIView):
    def post(self, request, courseid):
        messages = request.data["messages"]
        formatted_messages = list(map(lambda m: (m["sender"], m["message"]), messages))

        last_user_message = formatted_messages[-1][1]
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma(embedding_function=embeddings, persist_directory='courses_db', collection_name="course_content")
        results = vector_store.similarity_search(
            query=last_user_message,
            k=3,
            filter={"courseid": {"$in": [courseid]}},
    
        )
        source_knowledge = "\n".join([x.page_content for x in results])
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None
        )

        final_messages = [
            (
                    "system",
                    "You are a helpful assistant that helps the student clarify their doubts regarding the course.  Answer in less than 100 words. Added is some more context {source_knowledge}",
            ),
        ]
        final_messages.extend(formatted_messages)
        prompt = ChatPromptTemplate.from_messages(
            final_messages
        )

        chain = prompt | llm
        ai_msg = chain.invoke(
            {
                "source_knowledge": source_knowledge,
            }
        )
        return Response({"message": ai_msg.content}, status=status.HTTP_200_OK)