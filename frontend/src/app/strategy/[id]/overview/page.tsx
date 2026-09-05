import type { Metadata } from "next";
import OverviewPageClient from "./OverviewPageClient";

interface OverviewPageProps {
  params: Promise<{ id: string }>;
}

export const metadata: Metadata = { title: "Overview" };

export default async function OverviewPage({ params }: OverviewPageProps) {
  const { id } = await params;
  return <OverviewPageClient strategyId={id} />;
}
