from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import BankOfferSerializer, BankOfferListSerializer
from .models import BankOffer
from .tasks import parse_bank_offer_details

from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# Create your views here.
class BankOfferList(APIView):
    def post(self, request):
        serializer = BankOfferSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            ser = BankOfferListSerializer(obj)
            parse_bank_offer_details.delay(obj.boid, obj.offer_details_url)
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        limit = request.GET.get('limit', 10)
        bank_offers = BankOffer.objects.all()[:limit]
        serializer = BankOfferListSerializer(bank_offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class BankOfferChat(APIView):
    def post(self, request):
        messages = request.data["messages"]
        formatted_messages = list(map(lambda m: (m["sender"], m["message"]), messages))

        last_user_message = formatted_messages[-1][1]
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = Chroma(embedding_function=embeddings, persist_directory="bankoffers_db", collection_name="bank_offer_documents")
        results = vector_store.similarity_search(query=last_user_message, k=3)
        source_knowledge = "\n".join([x.page_content for x in results])
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None
        )

        final_messages = [
            (
                    "system",
                    "You are a helpful assistant that helps loan seekers clarify their doubts regarding the available bank loans. Answer in less than 100 words. Added is some more context {source_knowledge}",
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