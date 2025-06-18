import * as React from "react"
import { cn } from "../../lib/utils"
import { VariantProps, cva } from "class-variance-authority"

const inputVariants = cva(
  "flex w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground transition-all duration-200 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none",
        spiritual: "focus:border-spiritual-500 focus:ring-2 focus:ring-spiritual-500/20 focus:outline-none",
        error: "border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 focus:outline-none",
        success: "border-green-500 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 focus:outline-none",
      },
      inputSize: {
        sm: "h-8 px-2 text-xs",
        default: "h-10 px-3",
        lg: "h-12 px-4 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      inputSize: "default",
    },
  }
)

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size">,
    VariantProps<typeof inputVariants> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant, inputSize, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(inputVariants({ variant, inputSize, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input, inputVariants } 