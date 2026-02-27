import GridBackground from "@/components/GridBackground";
import { Input } from "@/components/ui/input";
import { Upload } from "lucide-react";
import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const HomePageDemo = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const navigator = useNavigate();

  const handleApiRequest = async () => {
    const formData = new FormData();

    // append all selected files
    files.forEach((file) => {
      formData.append("images", file);
    });

    setLoading(true);

    try {
      const res = await axios.post(
        "http://localhost:5000/predict-batch",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      navigator("/results-batch", {
        state: { batchResults: res.data },
      });

    } catch (error) {
      console.log(error);
    }

    setLoading(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files
      ? Array.from(e.target.files)
      : [];

    setFiles(selectedFiles);
  };

  useEffect(() => {
    if (files.length > 0) {
      handleApiRequest();
    }
  }, [files]);

  return (
    <div className="w-full h-full flex flex-col items-center justify-center overflow-hidden pt-52">
      {loading ? (
        <p className="z-50 flex flex-col items-center justify-center w-1/3 h-64 border-2 border-gray-300 border-dashed rounded-2xl cursor-pointer bg-gray-200">
          Processing Batch...
        </p>
      ) : (
        <div className="flex items-center justify-center z-10">
          <label
            htmlFor="dropzone-file"
            className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-2xl cursor-pointer bg-gray-50 hover:bg-gray-100"
          >
            <div className="flex flex-col items-center justify-center gap-4 pt-5 pb-6">
              <Upload className="w-8 text-gray-500" />
              <div className="flex flex-col items-center">
                <p className="mb-2 text-sm text-gray-500 px-64">
                  <span className="font-semibold">Click to upload multiple images</span>
                </p>
                <p className="text-xs text-gray-500">
                  JPG or JPEG
                </p>
              </div>
            </div>

            <Input
              id="dropzone-file"
              type="file"
              multiple
              className="hidden"
              onChange={handleFileChange}
            />
          </label>
        </div>
      )}

      <div className="absolute pt-16 pointer-events-none">
        <GridBackground />
      </div>
    </div>
  );
};

export default HomePageDemo;