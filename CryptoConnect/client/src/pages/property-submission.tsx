import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import PropertySubmissionForm from "@/components/forms/property-submission-form";
import type { PageView } from "@/pages/home-page";

interface PropertySubmissionProps {
  onNavigate: (page: PageView) => void;
}

export default function PropertySubmission({ onNavigate }: PropertySubmissionProps) {
  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Submit New Property</h2>
        <p className="text-muted-foreground">List your property for tokenized investment</p>
      </div>

      <PropertySubmissionForm onSuccess={() => onNavigate("my-properties")} />
    </div>
  );
}
