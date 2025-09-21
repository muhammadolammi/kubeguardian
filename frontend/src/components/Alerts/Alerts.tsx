import React, { useEffect, useState } from "react";
import { Alert, User } from '../../types';
import { BACKEND_URL } from "../../const"




interface AlertsProps {
    onLogout: () => void;
}

const Alerts: React.FC<AlertsProps> = ({ onLogout }) => {
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        const fetchUserAndAlerts = async () => {
            try {
                setIsLoading(true);

                // check auth
                const userRes = await fetch(`${BACKEND_URL}me`, {
                    credentials: "include",
                });
                if (!userRes.ok) {
                    window.location.href = "/login";
                    return;
                }
                const userData = await userRes.json();
                setUser(userData);

                // fetch alerts
                const res = await fetch(`${BACKEND_URL}custom-alerts`, {
                    credentials: "include",
                });
                if (!res.ok) throw new Error("Failed to fetch alerts");

                const data = await res.json();
                if (data["error encountered "]) {
                    console.log("error encountered")
                    return []
                }

                console.log(data)
                setAlerts(data);
            } catch (err: any) {
                setError(err.message || "Something went wrong");
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserAndAlerts();
    }, []);

    const handleLogout = async () => {
        try {
            await fetch(`${BACKEND_URL}logout`, {
                method: "POST",
                credentials: "include",
            });
        } catch (err) {
            console.error("Logout error:", err);
        } finally {
            onLogout();
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen bg-[#111418] text-white">
                Loading alerts...
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen bg-[#111418] text-red-500">
                {error}
            </div>
        );
    }

    return (
        <div
            className="relative flex size-full min-h-screen flex-col bg-[#111418] overflow-x-hidden"
            style={{ fontFamily: '"Space Grotesk", "Noto Sans", sans-serif' }}
        >
            {/* Header */}
            <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#283039] px-10 py-3">
                <div className="flex items-center gap-4 text-white">
                    <svg
                        className="size-8 text-[#1173d4]"
                        fill="none"
                        viewBox="0 0 48 48"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            clipRule="evenodd"
                            d="M39.475 21.6262C40.358 21.4363 40.6863 21.5589 40.7581 21.5934C40.7876 21.655 40.8547 21.857 40.8082 22.3336C40.7408 23.0255 40.4502 24.0046 39.8572 25.2301C38.6799 27.6631 36.5085 30.6631 33.5858 33.5858C30.6631 36.5085 27.6632 38.6799 25.2301 39.8572C24.0046 40.4502 23.0255 40.7407 22.3336 40.8082C21.8571 40.8547 21.6551 40.7875 21.5934 40.7581C21.5589 40.6863 21.4363 40.358 21.6262 39.475C21.8562 38.4054 22.4689 36.9657 23.5038 35.2817C24.7575 33.2417 26.5497 30.9744 28.7621 28.762C30.9744 26.5497 33.2417 24.7574 35.2817 23.5037C36.9657 22.4689 38.4054 21.8562 39.475 21.6262ZM4.41189 29.2403L18.7597 43.5881C19.8813 44.7097 21.4027 44.9179 22.7217 44.7893C24.0585 44.659 25.5148 44.1631 26.9723 43.4579C29.9052 42.0387 33.2618 39.5667 36.4142 36.4142C39.5667 33.2618 42.0387 29.9052 43.4579 26.9723C44.1631 25.5148 44.659 24.0585 44.7893 22.7217C44.9179 21.4027 44.7097 19.8813 43.5881 18.7597L29.2403 4.41187C27.8527 3.02428 25.8765 3.02573 24.2861 3.36776C22.6081 3.72863 20.7334 4.58419 18.8396 5.74801C16.4978 7.18716 13.9881 9.18353 11.5858 11.5858C9.18354 13.988 7.18717 16.4978 5.74802 18.8396C4.58421 20.7334 3.72865 22.6081 3.36778 24.2861C3.02574 25.8765 3.02429 27.8527 4.41189 29.2403Z"
                            fill="currentColor"
                            fillRule="evenodd"
                        />
                    </svg>
                    <h1 className="text-xl font-bold">KubeGuardian - Alerts</h1>
                </div>
                <div className="flex flex-1 justify-end gap-4">
                    <button
                        onClick={handleLogout}
                        className="rounded-md bg-[#283039] px-3 py-2 text-sm font-medium text-white hover:bg-[#1173d4]"
                    >
                        Logout
                    </button>
                </div>
            </header>

            {/* Alerts List */}
            <main className="flex-1 p-6 overflow-y-auto">
                {alerts.length === 0 ? (
                    <p className="text-gray-400 text-center mt-10">
                        🎉 No alerts at the moment
                    </p>
                ) : (
                    <div className="space-y-4">
                        {alerts.map((alert) => (
                            <div
                                key={alert.id}
                                className="rounded-lg bg-[#1c2127] p-5 shadow-md border border-[#283039]"
                            >
                                <div className="flex justify-between items-center mb-2">
                                    <h2 className="text-lg font-semibold text-white">
                                        ({alert.severity})
                                    </h2>
                                    <span className="text-sm text-gray-400">
                                        {new Date(alert.created_at).toLocaleString()}
                                    </span>
                                </div>
                                <p className="text-sm text-red-400 font-medium mb-1">
                                    Reason: {alert.description}
                                </p>
                                {/* <p className="text-sm text-gray-300 mb-2">{alert.body}</p> */}
                                {/* <div className="text-xs text-gray-400">
                        
                                    {alert.tier && <p>Tier: {alert.tier}</p>}
                                    {alert.labels && (
                                        <p>
                                            Labels:{" "}
                                            {Object.entries(alert.labels)
                                                .map(([k, v]) => `${k}=${v}`)
                                                .join(", ")}
                                        </p>
                                    )}
                                    {alert.extra && <p>Extra: {alert.extra}</p>}
                                </div> */}
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};

export default Alerts;