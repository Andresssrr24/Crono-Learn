import axiosInstance from "./axiosInstance";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

export const getStudyRecords = async () => {
  return axiosInstance.get(`${BACKEND_URL}my-studies`);
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

