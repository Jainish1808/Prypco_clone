import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Loader2, Upload, CheckCircle, ImageIcon } from "lucide-react";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface PropertySubmissionFormProps {
  onSuccess: () => void;
}

type FormData = {
  title: string;
  description: string;
  address: string;
  city: string;
  country: string;
  property_type: string;
  total_value: number;
  size_sqm: number;
  bedrooms?: number;
  bathrooms?: number;
  parking_spaces?: number;
  year_built?: number;
  monthly_rent?: number;
  images?: string[];
  acceptedTerms: boolean;
};

const formSchema = z.object({
  title: z.string().min(1, "Property title is required"),
  description: z
    .string()
    .min(1, "Description is required")
    .default("Property description"),
  address: z.string().min(1, "Address is required"),
  city: z.string().min(1, "City is required"),
  country: z.string().min(1, "Country is required"),
  property_type: z.string().min(1, "Property type is required"),
  total_value: z.number().min(1, "Property value must be greater than 0"),
  size_sqm: z.number().min(1, "Property size must be greater than 0"),
  bedrooms: z.number().optional(),
  bathrooms: z.number().optional(),
  parking_spaces: z.number().optional(),
  year_built: z.number().optional(),
  monthly_rent: z.number().optional(),
  images: z.array(z.string()).optional(),
  acceptedTerms: z.boolean().refine((val: boolean) => val === true, {
    message: "You must accept the terms and conditions",
  }),
});

export default function PropertySubmissionForm({
  onSuccess,
}: PropertySubmissionFormProps) {
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedImages, setUploadedImages] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const totalSteps = 4;

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      description: "",
      address: "",
      city: "",
      country: "",
      property_type: "apartment",
      total_value: 0,
      size_sqm: 0,
      bedrooms: 0,
      bathrooms: 0,
      parking_spaces: 0,
      year_built: new Date().getFullYear(),
      monthly_rent: 0,
      images: [],
      acceptedTerms: false,
    },
  });

  const watchedValues = form.watch();

  // Calculate tokenization preview
  const totalTokens = watchedValues.size_sqm
    ? watchedValues.size_sqm * 10000
    : 0;
  const tokenPrice =
    watchedValues.total_value && totalTokens
      ? watchedValues.total_value / totalTokens
      : 0;
  const minInvestment = tokenPrice ? tokenPrice * 100 : 0;

  const submitMutation = useMutation({
    mutationFn: async (data: FormData) => {
      console.log("=== PROPERTY SUBMISSION START ===");
      console.log("Submitting property data:", data);

      // Check authentication
      const token = localStorage.getItem("token");
      console.log("Token available:", !!token);

      const { acceptedTerms, ...propertyData } = data;

      // Ensure description is not empty
      if (!propertyData.description || propertyData.description.trim() === "") {
        propertyData.description = "Property description to be updated";
      }

      console.log("Final property data:", propertyData);
      console.log("Calling api.submitProperty...");

      try {
        const result = await api.submitProperty(propertyData);
        console.log("=== PROPERTY SUBMISSION SUCCESS ===");
        return result;
      } catch (error) {
        console.log("=== PROPERTY SUBMISSION ERROR ===");
        console.error("API call failed:", error);
        throw error;
      }
    },
    onSuccess: (data) => {
      console.log("Property submitted successfully:", data);
      toast({
        title: "Property Submitted",
        description:
          "Your property has been submitted for review successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/seller/properties"] });
      onSuccess();
    },
    onError: (error: Error) => {
      console.error("Property submission failed:", error);
      toast({
        title: "Submission Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleImageUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      const fileArray = Array.from(files);
      const result = await api.uploadImages(fileArray);

      const imageUrls = result.uploaded_files.map((file) => file.url);
      setUploadedImages((prev) => [...prev, ...imageUrls]);
      form.setValue("images", [...uploadedImages, ...imageUrls]);

      toast({
        title: "Images Uploaded",
        description: `${fileArray.length} image(s) uploaded successfully.`,
      });
    } catch (error) {
      toast({
        title: "Upload Failed",
        description:
          error instanceof Error ? error.message : "Failed to upload images",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = (data: FormData) => {
    console.log("🚀 FORM ONSUBMIT TRIGGERED!");
    console.log("Form submitted with data:", data);

    // Check if user is logged in
    const token = localStorage.getItem("token");
    console.log("Auth token exists:", !!token);
    console.log(
      "Token preview:",
      token ? token.substring(0, 50) + "..." : "No token"
    );

    // Validate required fields
    if (!data.title || !data.address || !data.city || !data.country) {
      console.error("Missing required fields!");
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    if (!data.acceptedTerms) {
      console.error("Terms not accepted!");
      toast({
        title: "Terms Required",
        description: "Please accept the terms and conditions",
        variant: "destructive",
      });
      return;
    }

    // Submit property
    console.log("🎯 Calling submitMutation.mutate...");
    submitMutation.mutate(data);
  };

  const progress = (currentStep / totalSteps) * 100;

  return (
    <Card className="w-full max-w-4xl mx-auto">
      {/* Progress Indicator */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            {Array.from({ length: totalSteps }, (_, i) => {
              const stepNumber = i + 1;
              const isActive = stepNumber === currentStep;
              const isCompleted = stepNumber < currentStep;

              return (
                <div key={stepNumber} className="flex items-center gap-2">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                      isCompleted
                        ? "bg-green-600 text-white"
                        : isActive
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {isCompleted ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      stepNumber
                    )}
                  </div>
                  {stepNumber < totalSteps && (
                    <div className="w-8 h-px bg-border" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
        <Progress value={progress} className="w-full" />
        <div className="flex justify-between text-sm text-muted-foreground mt-2">
          <span>
            Step {currentStep} of {totalSteps}
          </span>
          <span>{progress.toFixed(0)}% Complete</span>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <CardContent className="p-6">
            {/* Step 1: Basic Information */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">
                    Basic Property Information
                  </h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <FormField
                      control={form.control}
                      name="title"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Property Title</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="e.g., Luxury Dubai Marina Apartment"
                              data-testid="input-property-title"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="property_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Property Type</FormLabel>
                          <FormControl>
                            <Select
                              value={field.value}
                              onValueChange={field.onChange}
                            >
                              <SelectTrigger data-testid="select-property-type">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="apartment">
                                  Apartment
                                </SelectItem>
                                <SelectItem value="villa">Villa</SelectItem>
                                <SelectItem value="office">Office</SelectItem>
                                <SelectItem value="retail">Retail</SelectItem>
                                <SelectItem value="warehouse">
                                  Warehouse
                                </SelectItem>
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="address"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Street Address</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="Street address"
                              data-testid="input-property-address"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="city"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>City</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="e.g., Dubai"
                              data-testid="input-property-city"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="country"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Country</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              placeholder="e.g., UAE"
                              data-testid="input-property-country"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="total_value"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Property Value (AED)</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="number"
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                              placeholder="e.g., 2600000"
                              data-testid="input-property-value"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="size_sqm"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Property Size (sq m)</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="number"
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                              placeholder="e.g., 130"
                              data-testid="input-property-size"
                            />
                          </FormControl>
                          <p className="text-sm text-muted-foreground">
                            Total tokens will be calculated as: Size × 10,000
                          </p>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="monthly_rent"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Monthly Rent (AED)</FormLabel>
                          <FormControl>
                            <Input
                              {...field}
                              type="number"
                              onChange={(e) =>
                                field.onChange(Number(e.target.value))
                              }
                              placeholder="e.g., 12000"
                              data-testid="input-monthly-rent"
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Token Calculation Preview */}
                {totalTokens > 0 && (
                  <div className="p-4 bg-muted rounded-lg">
                    <h4 className="font-medium mb-3">
                      Token Calculation Preview
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Total Tokens</p>
                        <p className="font-semibold">
                          {totalTokens.toLocaleString()}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Size × 10,000
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Token Price</p>
                        <p className="font-semibold">
                          ${tokenPrice.toFixed(2)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Value ÷ Total Tokens
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Min. Investment</p>
                        <p className="font-semibold">
                          ${minInvestment.toFixed(2)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          100 tokens minimum
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Property Details */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">
                  Detailed Property Information
                </h3>

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Property Description</FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          rows={4}
                          placeholder="Describe the property, its features, location benefits, and investment potential..."
                          data-testid="textarea-property-description"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="bedrooms"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Bedrooms</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            onChange={(e) =>
                              field.onChange(Number(e.target.value))
                            }
                            placeholder="e.g., 2"
                            data-testid="input-bedrooms"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="bathrooms"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Bathrooms</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            onChange={(e) =>
                              field.onChange(Number(e.target.value))
                            }
                            placeholder="e.g., 2"
                            data-testid="input-bathrooms"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="parking_spaces"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Parking Spaces</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            onChange={(e) =>
                              field.onChange(Number(e.target.value))
                            }
                            placeholder="e.g., 1"
                            data-testid="input-parking-spaces"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="year_built"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Year Built</FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            type="number"
                            onChange={(e) =>
                              field.onChange(Number(e.target.value))
                            }
                            placeholder="e.g., 2015"
                            data-testid="input-year-built"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            )}

            {/* Step 3: Images */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Property Images</h3>
                <p className="text-muted-foreground">
                  Upload high-quality images of your property. You can upload up
                  to 10 images.
                </p>

                <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
                  <ImageIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-lg font-medium mb-2">
                    Upload Property Images
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    Drag and drop images here, or click to select files
                  </p>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="image-upload"
                    disabled={isUploading}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() =>
                      document.getElementById("image-upload")?.click()
                    }
                    disabled={isUploading}
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Choose Images
                      </>
                    )}
                  </Button>
                </div>

                {/* Display uploaded images */}
                {uploadedImages.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-3">
                      Uploaded Images ({uploadedImages.length})
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {uploadedImages.map((imageUrl, index) => (
                        <div key={index} className="relative">
                          <img
                            src={`http://localhost:8000${imageUrl}`}
                            alt={`Property image ${index + 1}`}
                            className="w-full h-24 object-cover rounded-lg border border-border"
                          />
                          <Button
                            type="button"
                            variant="destructive"
                            size="sm"
                            className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0"
                            onClick={() => {
                              const newImages = uploadedImages.filter(
                                (_, i) => i !== index
                              );
                              setUploadedImages(newImages);
                              form.setValue("images", newImages);
                            }}
                          >
                            ×
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 4: Review */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">
                  Review Your Submission
                </h3>

                {/* Property Summary */}
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Property Summary</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Property Title</p>
                      <p className="font-medium">
                        {watchedValues.title || "Not specified"}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Property Value</p>
                      <p className="font-medium">
                        AED {watchedValues.total_value?.toLocaleString() || "0"}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Size</p>
                      <p className="font-medium">
                        {watchedValues.size_sqm} sq m
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Monthly Rent</p>
                      <p className="font-medium">
                        AED{" "}
                        {watchedValues.monthly_rent?.toLocaleString() || "0"}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Location</p>
                      <p className="font-medium">
                        {watchedValues.city}, {watchedValues.country}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Property Type</p>
                      <p className="font-medium">
                        {watchedValues.property_type}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Tokenization Details */}
                <div className="bg-muted p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Tokenization Details</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Total Tokens</p>
                      <p className="font-bold text-primary">
                        {totalTokens.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Token Price</p>
                      <p className="font-bold text-secondary">
                        ${tokenPrice.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">
                        Minimum Investment
                      </p>
                      <p className="font-bold">${minInvestment.toFixed(2)}</p>
                    </div>
                  </div>
                </div>

                {/* Terms and Conditions */}
                <FormField
                  control={form.control}
                  name="acceptedTerms"
                  render={({ field }) => (
                    <FormItem
                      className={`flex flex-row items-start space-x-3 space-y-0 border rounded-lg p-4 ${
                        !field.value
                          ? "border-red-300 bg-red-50"
                          : "border-border"
                      }`}
                    >
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={(checked) => {
                            console.log("Terms checkbox changed:", checked);
                            field.onChange(checked);
                          }}
                          data-testid="checkbox-accept-terms"
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel
                          className={!field.value ? "text-red-600" : ""}
                        >
                          Terms and Conditions{" "}
                          {!field.value && (
                            <span className="text-red-500">*</span>
                          )}
                        </FormLabel>
                        <p className="text-sm text-muted-foreground">
                          I confirm that all information provided is accurate
                          and complete. I understand that this property will
                          undergo an internal review process before being
                          approved for tokenization and listing on the platform.
                        </p>
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-6 border-t border-border">
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
                data-testid="button-previous-step"
              >
                Previous
              </Button>

              {currentStep < totalSteps ? (
                <Button
                  type="button"
                  onClick={nextStep}
                  data-testid="button-next-step"
                >
                  Continue
                </Button>
              ) : (
                <div className="flex flex-col items-end gap-2">
                  {!watchedValues.acceptedTerms && (
                    <p className="text-sm text-red-500">
                      Please accept the terms and conditions to submit
                    </p>
                  )}
                  <Button
                    type="button"
                    disabled={
                      submitMutation.isPending || !watchedValues.acceptedTerms
                    }
                    data-testid="button-submit-property"
                    className="bg-primary hover:bg-primary/90 text-primary-foreground px-8 py-2"
                    onClick={() => {
                      console.log("🚀 SUBMITTING PROPERTY...");
                      const formData = form.getValues();
                      console.log("Form data:", formData);
                      onSubmit(formData);
                    }}
                  >
                    {submitMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      "Submit Property"
                    )}
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </form>
      </Form>
    </Card>
  );
}
