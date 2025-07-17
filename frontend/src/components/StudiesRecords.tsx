import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

interface StudiesRecordsProps {
    topic?: string; 
    study_time?: number; 
    notes: string;  
}