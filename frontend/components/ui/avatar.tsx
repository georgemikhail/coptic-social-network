import * as React from "react"
import { cn } from "../../lib/utils"
import { VariantProps, cva } from "class-variance-authority"

const avatarVariants = cva(
  "relative flex shrink-0 overflow-hidden rounded-full bg-gradient-to-br from-spiritual-400 to-spiritual-600 shadow-soft",
  {
    variants: {
      size: {
        sm: "h-8 w-8",
        default: "h-10 w-10",
        lg: "h-12 w-12",
        xl: "h-16 w-16",
        "2xl": "h-20 w-20",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const avatarImageVariants = cva("aspect-square h-full w-full object-cover")

const avatarFallbackVariants = cva(
  "flex h-full w-full items-center justify-center rounded-full text-white font-semibold",
  {
    variants: {
      size: {
        sm: "text-xs",
        default: "text-sm",
        lg: "text-base",
        xl: "text-lg",
        "2xl": "text-xl",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface AvatarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarVariants> {}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(avatarVariants({ size, className }))}
      {...props}
    />
  )
)
Avatar.displayName = "Avatar"

export interface AvatarImageProps
  extends React.ImgHTMLAttributes<HTMLImageElement> {}

const AvatarImage = React.forwardRef<HTMLImageElement, AvatarImageProps>(
  ({ className, ...props }, ref) => (
    <img
      ref={ref}
      className={cn(avatarImageVariants({ className }))}
      {...props}
    />
  )
)
AvatarImage.displayName = "AvatarImage"

export interface AvatarFallbackProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarFallbackVariants> {}

const AvatarFallback = React.forwardRef<HTMLDivElement, AvatarFallbackProps>(
  ({ className, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(avatarFallbackVariants({ size, className }))}
      {...props}
    />
  )
)
AvatarFallback.displayName = "AvatarFallback"

export { Avatar, AvatarImage, AvatarFallback } 