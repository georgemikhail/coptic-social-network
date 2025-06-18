import * as React from "react"
import { cn } from "../../lib/utils"
import { VariantProps, cva } from "class-variance-authority"
import { Search, X, Loader2 } from "lucide-react"
import { Input } from "./input"
import { Button } from "./button"

const searchBarVariants = cva(
  "relative w-full",
  {
    variants: {
      size: {
        sm: "max-w-sm",
        default: "max-w-md",
        lg: "max-w-lg",
        full: "w-full",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

export interface SearchResult {
  id: string
  title: string
  subtitle?: string
  type?: string
  icon?: React.ReactNode
}

export interface SearchBarProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "size" | "results">,
    VariantProps<typeof searchBarVariants> {
  results?: SearchResult[]
  isLoading?: boolean
  onSearch?: (query: string) => void
  onResultSelect?: (result: SearchResult) => void
  onClear?: () => void
  showClearButton?: boolean
  debounceMs?: number
}

const SearchBar = React.forwardRef<HTMLInputElement, SearchBarProps>(
  ({ 
    className, 
    size, 
    results = [], 
    isLoading = false,
    onSearch,
    onResultSelect,
    onClear,
    showClearButton = true,
    debounceMs = 300,
    placeholder = "Search...",
    ...props 
  }, ref) => {
    const [query, setQuery] = React.useState("")
    const [isOpen, setIsOpen] = React.useState(false)
    const [selectedIndex, setSelectedIndex] = React.useState(-1)
    const searchRef = React.useRef<HTMLInputElement>(null)
    const resultsRef = React.useRef<HTMLDivElement>(null)

    // Debounced search
    React.useEffect(() => {
      const timer = setTimeout(() => {
        if (query.trim() && onSearch) {
          onSearch(query.trim())
        }
      }, debounceMs)

      return () => clearTimeout(timer)
    }, [query, onSearch, debounceMs])

    // Handle keyboard navigation
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (!isOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setSelectedIndex(prev => 
            prev < results.length - 1 ? prev + 1 : prev
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
          break
        case 'Enter':
          e.preventDefault()
          if (selectedIndex >= 0 && results[selectedIndex]) {
            handleResultSelect(results[selectedIndex])
          }
          break
        case 'Escape':
          setIsOpen(false)
          setSelectedIndex(-1)
          searchRef.current?.blur()
          break
      }
    }

    const handleResultSelect = (result: SearchResult) => {
      setQuery(result.title)
      setIsOpen(false)
      setSelectedIndex(-1)
      onResultSelect?.(result)
    }

    const handleClear = () => {
      setQuery("")
      setIsOpen(false)
      setSelectedIndex(-1)
      onClear?.()
      searchRef.current?.focus()
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value
      setQuery(value)
      setIsOpen(value.trim().length > 0)
      setSelectedIndex(-1)
    }

    // Close results when clicking outside
    React.useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (resultsRef.current && !resultsRef.current.contains(event.target as Node)) {
          setIsOpen(false)
          setSelectedIndex(-1)
        }
      }

      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    return (
      <div className={cn(searchBarVariants({ size, className }))}>
        <div className="relative">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4 z-10" />
            <Input
              ref={searchRef}
              value={query}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => query.trim() && setIsOpen(true)}
              placeholder={placeholder}
              className="pl-10 pr-20"
              {...props}
            />
            
            {/* Loading/Clear Button */}
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
              {isLoading && (
                <Loader2 className="w-4 h-4 text-muted-foreground animate-spin" />
              )}
              {showClearButton && query && !isLoading && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 hover:bg-muted"
                  onClick={handleClear}
                >
                  <X className="w-3 h-3" />
                </Button>
              )}
            </div>
          </div>

          {/* Search Results */}
          {isOpen && (query.trim() || results.length > 0) && (
            <div 
              ref={resultsRef}
              className="absolute top-full left-0 right-0 mt-1 bg-background border border-border rounded-lg shadow-large z-50 max-h-96 overflow-y-auto"
            >
              {results.length > 0 ? (
                <div className="py-2">
                  {results.map((result, index) => (
                    <button
                      key={result.id}
                      className={cn(
                        "w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors",
                        selectedIndex === index && "bg-muted/50"
                      )}
                      onClick={() => handleResultSelect(result)}
                      onMouseEnter={() => setSelectedIndex(index)}
                    >
                      {result.icon && (
                        <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-muted rounded-full">
                          {result.icon}
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">
                          {result.title}
                        </p>
                        {result.subtitle && (
                          <p className="text-xs text-muted-foreground truncate">
                            {result.subtitle}
                          </p>
                        )}
                      </div>
                      {result.type && (
                        <span className="flex-shrink-0 text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                          {result.type}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              ) : query.trim() && !isLoading ? (
                <div className="py-8 text-center">
                  <p className="text-sm text-muted-foreground">
                    No results found for "{query}"
                  </p>
                </div>
              ) : isLoading ? (
                <div className="py-8 text-center">
                  <Loader2 className="w-6 h-6 text-muted-foreground animate-spin mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Searching...</p>
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>
    )
  }
)
SearchBar.displayName = "SearchBar"

export { SearchBar } 