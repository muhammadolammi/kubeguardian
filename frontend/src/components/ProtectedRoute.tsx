// src/components/ProtectedRoute.tsx
import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { User } from "../types";
const BACKEND_URL = "http://localhost:8081";


const getCurrentUser = async (): Promise<User | null> => {
    try {
        const res = await fetch(`${BACKEND_URL}/me`, { credentials: "include" });
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
};

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        const fetchUser = async () => {
            const u = await getCurrentUser();
            setUser(u);
            setLoading(false);
        };
        fetchUser();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (!user) return <Navigate to="/auth" />;

    return <>{children}</>;
};

export default ProtectedRoute;
