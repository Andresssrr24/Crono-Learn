import axiosInstance from "./axiosInstance";

export const getStudyRecords = async () => {
    return axiosInstance.get('/study-records')
}

export const deleteRecord = async (record_id: number) => {
    return axiosInstance.delete(`/study-records/${record_id}/`);
}
