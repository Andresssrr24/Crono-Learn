import { PomodoroTimer } from "../components/PomodoroTimer"

export function PomodoroPage() {
    return (
        <div className="min-h-screen flex-col justify-center">
            <h1 className="text-4xl flex font-bold items-center justify-center">Pomodoro page</h1>
            <div className="p-10 flex justify-center">
                <PomodoroTimer timer={30} rest_time={30} task_name=""/>
            </div>    
        </div>
    )
}