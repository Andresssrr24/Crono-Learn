import { useState, useEffect } from 'react';

interface PomodoroTimerProps {
  initialSeconds: number;
}

export function PomodoroTimer({ initialSeconds }: PomodoroTimerProps) {
  const [secondsLeft, setSecondsLeft] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isRunning || secondsLeft <= 0) return;

    const intervalId = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(intervalId);
  }, [isRunning, secondsLeft]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = time % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleStartPause = () => {
    if (secondsLeft > 0) {
      setIsRunning((prev) => !prev);
    }
  };

  const handleReset = () => {
    setIsRunning(false);
    setSecondsLeft(initialSeconds);
  };

  const getStatus = () => {
    if (secondsLeft === 0) return "Completed";
    return isRunning ? "Running" : "Paused";
  };

  return (
    <div className="flex flex-col items-center gap-4 text-center bg-stone-900 text-white p-6 rounded-2xl w-80 shadow-md">
      <h2 className="text-2xl font-bold">Pomodoro Timer</h2>
      <p className="text-4xl font-mono">{formatTime(secondsLeft)}</p>
      <p className="text-sm text-emerald-400">Status: {getStatus()}</p>
      <div className="flex gap-4 mt-4">
        <button
          onClick={handleStartPause}
          className="bg-emerald-700 hover:bg-emerald-600 px-4 py-2 rounded-lg"
        >
          {isRunning ? 'Pause' : 'Start'}
        </button>
        <button
          onClick={handleReset}
          className="bg-red-600 hover:bg-red-500 px-4 py-2 rounded-lg"
        >
          Reset
        </button>
      </div>
      {secondsLeft === 0 && <p className="text-yellow-400 mt-2">⏰ Time's up!</p>}
    </div>
  );
}

