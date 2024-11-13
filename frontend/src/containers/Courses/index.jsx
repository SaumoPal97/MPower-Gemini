import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { useState, useEffect, useRef } from "react";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { API_URL } from "@/lib/utils";
import BotChat from "@/components/BotChat";

import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function Courses() {
  const [height, setHeight] = useState(0);
  const ref = useRef(null);
  useEffect(() => {
    setHeight(
      window.innerHeight - ref.current.getBoundingClientRect().top - 60
    );
  }, [setHeight]);

  const navigate = useNavigate();

  const [courseTitle, setCourseTitle] = useState("");
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const getCourses = async () => {
      const response = await fetch(`${API_URL}/v1/api/courses/`);
      const res = await response.json();
      setCourses(res);
    };
    getCourses();
  }, []);

  const createCourse = async () => {
    try {
      await fetch(`${API_URL}/v1/api/courses/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: courseTitle,
        }),
      });
      toast.info("Course Creation in Progress...Check in sometime!");
      setCourseTitle("");
    } catch {
      toast.error("Course Creation Failed");
    }
  };

  return (
    <>
      <ToastContainer />
      <div className="h-full grid grid-cols-6 gap-3">
        <div className="flex flex-col col-span-4">
          <p className="font-bold text-2xl leading-none mb-5">Your Courses</p>
          <div className="grid grid-cols-3 grid-flow-rows gap-4">
            {courses.map((course) => {
              return (
                <Card key={course.id}>
                  <CardContent className="w-full h-48">
                    <img
                      className="h-full w-full object-cover"
                      src={course.image_url}
                    />
                  </CardContent>
                  <CardFooter className="flex flex-row justify-between">
                    <p className="text-lg">{course.title}</p>
                    <Button
                      onClick={() =>
                        navigate(`/course/${course.courseid}/chapter/0`)
                      }
                    >
                      Start
                    </Button>
                  </CardFooter>
                </Card>
              );
            })}
          </div>
        </div>
        <div className="flex flex-col col-span-2">
          <p className="font-bold text-2xl leading-none mb-5 text-center">
            ✨ Create Course with AI✨
          </p>
          <div className="flex flex-row my-1 overflow-y-none">
            <Input
              type="text"
              placeholder="What do you want to learn today?"
              value={courseTitle}
              className="mr-1"
              onChange={(e) => setCourseTitle(e.target.value)}
            />
            <Button onClick={createCourse}>Create</Button>
          </div>
          <p
            ref={ref}
            className="font-bold text-2xl leading-none mt-10 text-center mb-5"
          >
            Or Use our AI assistant for getting course suggestions below
          </p>
          <BotChat
            style={{ height }}
            chatEndpoint="/v1/api/courses/suggested/"
          />
        </div>
      </div>
    </>
  );
}

export default Courses;
