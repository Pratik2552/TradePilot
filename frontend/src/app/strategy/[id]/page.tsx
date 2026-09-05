import { redirect } from "next/navigation";
import { ROUTES } from "@/lib/constants";

interface StrategyIndexProps {
  params: Promise<{ id: string }>;
}

// Redirect /strategy/[id] → /strategy/[id]/overview
export default async function StrategyIndex({ params }: StrategyIndexProps) {
  const { id } = await params;
  redirect(ROUTES.STRATEGY_OVERVIEW(id));
}
