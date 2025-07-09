import { PomodoroTimer } from "../components/PomodoroTimer"

export function PomodoroPage() {
    return (
        <div className="flex">
            <h1 className="text-4xl flex font-bold">Pomodoro page</h1>
            <div className="p-10 flex">
                <PomodoroTimer initialSeconds={3600} />
            </div>    
        </div>
    )
}