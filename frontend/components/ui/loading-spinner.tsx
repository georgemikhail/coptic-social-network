import * as React from "react"
import { cn } from "../../lib/utils"
import { VariantProps, cva } from "class-variance-authority"

const spinnerVariants = cva(
  "animate-spin rounded-full border-2 border-transparent",
  {
    variants: {
      variant: {
        default: "border-t-primary-500 border-r-primary-500",
        spiritual: "border-t-spiritual-500 border-r-spiritual-500",
        muted: "border-t-muted-foreground border-r-muted-foreground",
      },
      size: {
        sm: "h-4 w-4",
        default: "h-6 w-6",
        lg: "h-8 w-8",
        xl: "h-12 w-12",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface LoadingSpinnerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof spinnerVariants> {
  label?: string
}

const LoadingSpinner = React.forwardRef<HTMLDivElement, LoadingSpinnerProps>(
  ({ className, variant, size, label, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center justify-center", className)}
      {...props}
    >
      <div className={cn(spinnerVariants({ variant, size }))} />
      {label && (
        <span className="ml-2 text-sm text-muted-foreground">{label}</span>
      )}
    </div>
  )
)
LoadingSpinner.displayName = "LoadingSpinner"

export { LoadingSpinner } 