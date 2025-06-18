import * as React from "react"
import { cn } from "../../lib/utils"
import { VariantProps, cva } from "class-variance-authority"
import { X } from "lucide-react"
import { Button } from "./button"

const modalVariants = cva(
  "fixed inset-0 z-50 flex items-center justify-center p-4",
  {
    variants: {
      variant: {
        default: "",
        centered: "items-center",
        top: "items-start pt-16",
      },
    },
    defaultVariants: {
      variant: "centered",
    },
  }
)

const modalContentVariants = cva(
  "relative w-full max-w-lg mx-auto bg-background border border-border rounded-lg shadow-large transition-all duration-200",
  {
    variants: {
      size: {
        sm: "max-w-sm",
        default: "max-w-lg",
        lg: "max-w-2xl",
        xl: "max-w-4xl",
        full: "max-w-full mx-4",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface ModalProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof modalVariants> {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
}

export interface ModalContentProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof modalContentVariants> {}

export interface ModalHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  showCloseButton?: boolean
  onClose?: () => void
}

export interface ModalBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

export interface ModalFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

const Modal = React.forwardRef<HTMLDivElement, ModalProps>(
  ({ className, variant, isOpen, onClose, children, ...props }, ref) => {
    React.useEffect(() => {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose()
        }
      }

      if (isOpen) {
        document.addEventListener('keydown', handleEscape)
        document.body.style.overflow = 'hidden'
      }

      return () => {
        document.removeEventListener('keydown', handleEscape)
        document.body.style.overflow = 'unset'
      }
    }, [isOpen, onClose])

    if (!isOpen) return null

    return (
      <div
        ref={ref}
        className={cn(modalVariants({ variant, className }))}
        {...props}
      >
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />
        
        {/* Content */}
        <div className="relative z-10 w-full max-w-lg mx-auto">
          {children}
        </div>
      </div>
    )
  }
)
Modal.displayName = "Modal"

const ModalContent = React.forwardRef<HTMLDivElement, ModalContentProps>(
  ({ className, size, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(modalContentVariants({ size, className }))}
      {...props}
    >
      {children}
    </div>
  )
)
ModalContent.displayName = "ModalContent"

const ModalHeader = React.forwardRef<HTMLDivElement, ModalHeaderProps>(
  ({ className, title, showCloseButton = true, onClose, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center justify-between p-6 border-b border-border", className)}
      {...props}
    >
      <div className="flex-1">
        {title && (
          <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        )}
        {children}
      </div>
      {showCloseButton && onClose && (
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0 ml-4"
          onClick={onClose}
        >
          <X className="w-4 h-4" />
        </Button>
      )}
    </div>
  )
)
ModalHeader.displayName = "ModalHeader"

const ModalBody = React.forwardRef<HTMLDivElement, ModalBodyProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("p-6", className)}
      {...props}
    >
      {children}
    </div>
  )
)
ModalBody.displayName = "ModalBody"

const ModalFooter = React.forwardRef<HTMLDivElement, ModalFooterProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center justify-end space-x-3 p-6 border-t border-border bg-muted/30", className)}
      {...props}
    >
      {children}
    </div>
  )
)
ModalFooter.displayName = "ModalFooter"

export { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } 