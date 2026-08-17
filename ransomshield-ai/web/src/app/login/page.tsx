"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ShieldAlert, Lock, User, Loader2, AlertTriangle } from "lucide-react";
import { useAuthStore } from "@/store/useAuthStore";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
      });

      if (!res.ok) {
        throw new Error("Invalid credentials or server offline");
      }

      const data = await res.json();
      
      // Decode JWT to extract role (Basic Base64 decode for frontend)
      const tokenPayload = JSON.parse(atob(data.access_token.split('.')[1]));
      
      setAuth(data.access_token, tokenPayload.role);
      router.push("/dashboard");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8 relative overflow-hidden bg-background">
      <div className="absolute inset-0 pointer-events-none" />
      
      <div className="enterprise-panel w-full max-w-md p-8 relative z-10 flex flex-col gap-6">
        <div className="flex flex-col items-center gap-4 border-b border-panel-border pb-6">
          <div className="p-4 bg-cyber-cyan/10 rounded-full">
            <ShieldAlert className="h-10 w-10 text-cyber-cyan" />
          </div>
          <h1 className="text-2xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyber-cyan to-cyber-purple">
            RANSOMSHIELD AI
          </h1>
          <p className="text-sm text-gray-400">Authorized Personnel Only</p>
        </div>

        <form onSubmit={handleLogin} className="flex flex-col gap-4 mt-2">
          {error && (
            <div className="p-3 rounded bg-alert-red/20 border border-alert-red/50 flex items-center gap-2 text-alert-red text-sm">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          <div className="relative">
            <User className="absolute left-3 top-3 h-5 w-5 text-gray-500" />
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-black/50 border border-panel-border rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-cyber-cyan transition-colors"
              required
            />
          </div>

          <div className="relative">
            <Lock className="absolute left-3 top-3 h-5 w-5 text-gray-500" />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-black/50 border border-panel-border rounded-lg py-3 pl-10 pr-4 text-white focus:outline-none focus:border-cyber-cyan transition-colors"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-4 py-3 rounded-lg flex items-center justify-center gap-2 font-bold transition-all bg-cyber-cyan text-black shadow-[0_0_15px_rgba(6,182,212,0.5)] hover:shadow-[0_0_25px_rgba(6,182,212,0.8)] disabled:opacity-50"
          >
            {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : "AUTHENTICATE"}
          </button>
        </form>
      </div>
    </div>
  );
}
