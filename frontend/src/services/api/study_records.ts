import axiosInstance from "./axiosInstance";

export const getStudyRecords = async () => {
  return axiosInstance.get("/my-studies");
};

export const createStudyRecord = async (data: {
  topic?: string | null;
  study_time: number;
  notes?: string | null;
}) => {
  return axiosInstance.post("/my-studies", data);
};

export const deleteRecord = async (record_id: number) => {
  return axiosInstance.delete(`/my-studies/${record_id}/`);
};

