import type { Metadata } from "next";
import PortfolioPageClient from "./PortfolioPageClient";

export const metadata: Metadata = { title: "Portfolio" };

interface PortfolioPageProps {
  params: Promise<{ id: string }>;
}

export default async function PortfolioPage({ params }: PortfolioPageProps) {
  const { id } = await params;
  return <PortfolioPageClient strategyId={id} />;
}
