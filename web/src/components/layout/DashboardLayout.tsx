import { ReactNode } from "react";
import Sidebar from "./Sidebar";
import ProtectedRoute from "../auth/ProtectedRoute";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="flex h-screen w-full overflow-hidden bg-background">
        <Sidebar />
        <main className="flex-1 flex flex-col overflow-y-auto relative">
          <div className="absolute inset-0 bg-gradient-to-br from-cyber-cyan/5 to-cyber-purple/5 pointer-events-none" />
          <div className="relative z-10 p-8 h-full">
            {children}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
