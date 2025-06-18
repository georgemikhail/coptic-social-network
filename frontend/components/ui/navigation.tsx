'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/router'
import { Button } from './button'
import { Badge } from './badge'
import { cn } from '../../lib/utils'

interface NavigationItem {
  href: string
  label: string
  icon?: React.ReactNode
  badge?: string | number
  external?: boolean
}

interface NavigationProps {
  items: NavigationItem[]
  brand?: {
    name: string
    href: string
    logo?: React.ReactNode
  }
  user?: {
    name: string
    avatar?: string
    email?: string
  }
  onUserMenuClick?: () => void
  className?: string
}

export function Navigation({ 
  items, 
  brand, 
  user, 
  onUserMenuClick, 
  className 
}: NavigationProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const router = useRouter()

  const isActive = (href: string) => router.pathname === href || router.pathname.startsWith(href + '/')

  return (
    <nav className={cn(
      "sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
      className
    )}>
      <div className="content-container">
        <div className="flex h-16 items-center justify-between">
          {/* Brand */}
          {brand && (
            <Link 
              href={brand.href}
              className="flex items-center space-x-2 font-bold text-xl transition-colors hover:text-primary-600"
            >
              {brand.logo}
              <span className="gradient-text">{brand.name}</span>
            </Link>
          )}

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center space-x-2 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200 hover:bg-accent hover:text-accent-foreground",
                  isActive(item.href) 
                    ? "bg-accent text-accent-foreground shadow-sm" 
                    : "text-muted-foreground"
                )}
              >
                {item.icon}
                <span>{item.label}</span>
                {item.badge && (
                  <Badge variant="secondary" className="ml-1 text-xs">
                    {item.badge}
                  </Badge>
                )}
              </Link>
            ))}
          </div>

          {/* User Menu & Mobile Toggle */}
          <div className="flex items-center space-x-2">
            {/* User Avatar */}
            {user && (
              <Button
                variant="ghost"
                className="relative h-10 w-10 rounded-full p-0"
                onClick={onUserMenuClick}
              >
                {user.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="h-full w-full rounded-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center rounded-full bg-primary-100 text-primary-700 font-medium">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                )}
              </Button>
            )}

            {/* Mobile Menu Toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label="Toggle mobile menu"
            >
              <svg
                className={cn(
                  "h-5 w-5 transition-transform duration-200",
                  isMobileMenuOpen && "rotate-90"
                )}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={isMobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
                />
              </svg>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-border/40 bg-background/95 backdrop-blur py-4 animate-slide-down">
            <div className="space-y-2">
              {items.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive(item.href)
                      ? "bg-accent text-accent-foreground"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  )}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <div className="flex items-center space-x-2">
                    {item.icon}
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <Badge variant="secondary" className="text-xs">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

// Breadcrumb Navigation
interface BreadcrumbItem {
  label: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  className?: string
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn("flex items-center space-x-1 text-sm text-muted-foreground", className)}>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {item.href ? (
            <Link
              href={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  )
} 