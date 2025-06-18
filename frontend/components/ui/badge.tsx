import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary-100 text-primary-800 hover:bg-primary-200",
        secondary: "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive: "border-transparent bg-red-100 text-red-800 hover:bg-red-200",
        outline: "text-foreground border-border hover:bg-accent",
        success: "border-transparent bg-green-100 text-green-800 hover:bg-green-200",
        warning: "border-transparent bg-yellow-100 text-yellow-800 hover:bg-yellow-200",
        spiritual: "border-transparent bg-spiritual-100 text-spiritual-800 hover:bg-spiritual-200",
        // Privacy level specific variants
        public: "border-transparent bg-green-100 text-green-800",
        parish_only: "border-transparent bg-blue-100 text-blue-800",
        private: "border-transparent bg-yellow-100 text-yellow-800",
        invite_only: "border-transparent bg-red-100 text-red-800",
        // Role specific variants
        admin: "border-transparent bg-red-100 text-red-800",
        moderator: "border-transparent bg-orange-100 text-orange-800",
        member: "border-transparent bg-neutral-100 text-neutral-800",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants } 