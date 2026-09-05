import type { Metadata } from "next";
import TradesPageClient from "./TradesPageClient";

export const metadata: Metadata = { title: "Trades" };

interface TradesPageProps {
  params: Promise<{ id: string }>;
}

export default async function TradesPage({ params }: TradesPageProps) {
  const { id } = await params;
  return <TradesPageClient strategyId={id} />;
}
