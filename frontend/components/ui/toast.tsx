import * as React from "react"
import { cn } from "../../lib/utils"
import { VariantProps, cva } from "class-variance-authority"
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react"
import { Button } from "./button"

const toastVariants = cva(
  "relative flex items-start space-x-3 p-4 rounded-lg border shadow-soft backdrop-blur-sm transition-all duration-300 ease-in-out",
  {
    variants: {
      variant: {
        default: "bg-background border-border text-foreground",
        success: "bg-green-50 border-green-200 text-green-900",
        error: "bg-red-50 border-red-200 text-red-900",
        warning: "bg-yellow-50 border-yellow-200 text-yellow-900",
        info: "bg-blue-50 border-blue-200 text-blue-900",
        spiritual: "bg-spiritual-50 border-spiritual-200 text-spiritual-900",
      },
      size: {
        sm: "text-sm",
        default: "",
        lg: "text-lg p-6",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const toastIconVariants = cva("flex-shrink-0 w-5 h-5", {
  variants: {
    variant: {
      default: "text-muted-foreground",
      success: "text-green-600",
      error: "text-red-600",
      warning: "text-yellow-600",
      info: "text-blue-600",
      spiritual: "text-spiritual-600",
    },
  },
  defaultVariants: {
    variant: "default",
  },
})

export interface ToastProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof toastVariants> {
  title?: string
  description?: string
  action?: React.ReactNode
  onClose?: () => void
  autoClose?: boolean
  duration?: number
  showIcon?: boolean
}

const getIcon = (variant: string) => {
  switch (variant) {
    case 'success':
      return CheckCircle
    case 'error':
      return AlertCircle
    case 'warning':
      return AlertTriangle
    case 'info':
      return Info
    case 'spiritual':
      return () => <span className="text-lg">🙏</span>
    default:
      return Info
  }
}

const Toast = React.forwardRef<HTMLDivElement, ToastProps>(
  ({ 
    className, 
    variant = "default",
    size,
    title, 
    description, 
    action,
    onClose,
    autoClose = true,
    duration = 5000,
    showIcon = true,
    children,
    ...props 
  }, ref) => {
    const [isVisible, setIsVisible] = React.useState(true)
    const timeoutRef = React.useRef<NodeJS.Timeout>()

    React.useEffect(() => {
      if (autoClose && duration > 0) {
        timeoutRef.current = setTimeout(() => {
          handleClose()
        }, duration)
      }

      return () => {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current)
        }
      }
    }, [autoClose, duration])

    const handleClose = () => {
      setIsVisible(false)
      setTimeout(() => {
        onClose?.()
      }, 300) // Wait for exit animation
    }

    const Icon = getIcon(variant || "default")

    if (!isVisible) {
      return null
    }

    return (
      <div
        ref={ref}
        className={cn(
          toastVariants({ variant, size, className }),
          "animate-in slide-in-from-right-full",
          !isVisible && "animate-out slide-out-to-right-full"
        )}
        {...props}
      >
        {/* Icon */}
        {showIcon && (
          <div className={cn(toastIconVariants({ variant }))}>
            <Icon className="w-5 h-5" />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="text-sm font-semibold leading-none tracking-tight mb-1">
              {title}
            </h4>
          )}
          {description && (
            <p className="text-sm opacity-90 leading-relaxed">
              {description}
            </p>
          )}
          {children}
          {action && (
            <div className="mt-3">
              {action}
            </div>
          )}
        </div>

        {/* Close Button */}
        {onClose && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0 opacity-70 hover:opacity-100"
            onClick={handleClose}
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>
    )
  }
)
Toast.displayName = "Toast"

// Toast Container for managing multiple toasts
export interface ToastContainerProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
  maxToasts?: number
}

const toastPositionClasses = {
  'top-right': 'top-4 right-4',
  'top-left': 'top-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
  'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2',
}

const ToastContainer: React.FC<ToastContainerProps & { children: React.ReactNode }> = ({
  position = 'top-right',
  maxToasts = 5,
  children
}) => {
  return (
    <div
      className={cn(
        "fixed z-50 flex flex-col space-y-2 w-full max-w-sm",
        toastPositionClasses[position]
      )}
    >
      {children}
    </div>
  )
}

// Toast hook for easy usage
export interface ToastOptions extends Omit<ToastProps, 'onClose'> {
  id?: string
}

export const useToast = () => {
  const [toasts, setToasts] = React.useState<(ToastOptions & { id: string })[]>([])

  const toast = React.useCallback((options: ToastOptions) => {
    const id = options.id || Math.random().toString(36).substr(2, 9)
    const newToast = { ...options, id }
    
    setToasts(prev => [...prev.slice(-(4)), newToast]) // Keep only last 5 toasts
    
    return id
  }, [])

  const dismiss = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const dismissAll = React.useCallback(() => {
    setToasts([])
  }, [])

  // Convenience methods
  const success = React.useCallback((title: string, description?: string) => {
    return toast({ variant: 'success', title, description })
  }, [toast])

  const error = React.useCallback((title: string, description?: string) => {
    return toast({ variant: 'error', title, description })
  }, [toast])

  const warning = React.useCallback((title: string, description?: string) => {
    return toast({ variant: 'warning', title, description })
  }, [toast])

  const info = React.useCallback((title: string, description?: string) => {
    return toast({ variant: 'info', title, description })
  }, [toast])

  const spiritual = React.useCallback((title: string, description?: string) => {
    return toast({ variant: 'spiritual', title, description })
  }, [toast])

  return {
    toasts,
    toast,
    success,
    error,
    warning,
    info,
    spiritual,
    dismiss,
    dismissAll,
  }
}

export { Toast, ToastContainer } 