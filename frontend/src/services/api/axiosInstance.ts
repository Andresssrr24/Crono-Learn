import axios from "axios";
import { supabase } from "../supabase";

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000/",
  withCredentials: false,
});

axiosInstance.interceptors.request.use(async (config) => {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;