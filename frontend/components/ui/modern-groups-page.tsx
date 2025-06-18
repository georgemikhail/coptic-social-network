'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardFooter, CardHeader } from './card'
import { Button } from './button'
import { Badge } from './badge'
import { Input } from './input'
import { groupsAPI, Group } from '../../lib/api'
import { cn } from '../../lib/utils'

// Modern group type icons with better styling
const GROUP_TYPE_ICONS = {
  ministry: '⛪',
  committee: '🏛️',
  study: '📚',
  prayer: '🙏',
  service: '🤝',
  social: '🎉',
  age_based: '👥',
  interest: '🔗'
}

interface ModernGroupCardProps {
  group: Group
  userMembership?: { role: 'admin' | 'moderator' | 'member' } | null
  onJoin: (groupId: string) => void
  onLeave: (groupId: string) => void
  isLoading?: boolean
}

function ModernGroupCard({ 
  group, 
  userMembership, 
  onJoin, 
  onLeave, 
  isLoading = false 
}: ModernGroupCardProps) {
  const isMember = !!userMembership
  const canJoin = !isMember && (group.privacy_level === 'public' || group.privacy_level === 'parish_only')

  return (
    <Card className="group overflow-hidden hover:shadow-large transition-all duration-300 hover:-translate-y-1 border-border/50">
      {/* Modern Cover Image */}
      {group.cover_image && (
        <div className="relative h-48 overflow-hidden">
          <img 
            src={group.cover_image} 
            alt={group.name}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
          
          {/* Privacy Badge with Glass Effect */}
          <div className="absolute top-4 right-4">
            <Badge 
              variant={group.privacy_level as any} 
              className="glass backdrop-blur-md bg-white/90 border-white/20"
            >
              {group.privacy_level.replace('_', ' ')}
            </Badge>
          </div>
        </div>
      )}
      
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            {/* Modern Icon Background */}
            <div className="p-3 rounded-xl bg-gradient-to-br from-spiritual-100 to-spiritual-200 text-spiritual-700 text-xl shadow-soft">
              {GROUP_TYPE_ICONS[group.group_type]}
            </div>
            <div>
              <h3 className="font-semibold text-foreground text-lg leading-tight">
                {group.name}
              </h3>
              <p className="text-muted-foreground capitalize font-medium text-sm">
                {group.group_type.replace('_', ' ')}
              </p>
            </div>
          </div>
          
          {/* Role Badge */}
          {isMember && (
            <Badge variant={userMembership.role as any}>
              {userMembership.role}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="pb-4">
        <p className="text-muted-foreground leading-relaxed line-clamp-3 mb-6">
          {group.description}
        </p>

        {/* Modern Stats Display */}
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-spiritual-400 rounded-full"></div>
              <span className="text-muted-foreground">{group.member_count} members</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-primary-400 rounded-full"></div>
              <span className="text-muted-foreground">{group.post_count} posts</span>
            </div>
          </div>
          <Badge variant="outline" className="text-xs">
            {group.parish.name}
          </Badge>
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-between pt-4 border-t border-border">
        {/* Modern Link with Animation */}
        <Link 
          href={`/groups/${group.id}`}
          className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium text-sm transition-all duration-200 group"
        >
          <span>View Details</span>
          <svg className="w-4 h-4 transition-transform duration-200 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
        
        {/* Modern Action Buttons */}
        <div className="flex space-x-2">
          {isMember ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onLeave(group.id)}
              disabled={isLoading}
              className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-colors"
            >
              Leave
            </Button>
          ) : canJoin ? (
            <Button
              variant="spiritual"
              size="sm"
              onClick={() => onJoin(group.id)}
              disabled={isLoading}
            >
              Join Group
            </Button>
          ) : (
            <Badge variant="outline" className="px-3 py-1.5">
              {group.privacy_level === 'private' ? 'Private' : 'Invite Only'}
            </Badge>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}

export default function ModernGroupsPage() {
  const [activeTab, setActiveTab] = useState<'discover' | 'my-groups'>('discover')
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState<string>('')
  const [selectedPrivacy, setSelectedPrivacy] = useState<string>('')

  // Load groups function
  const loadGroups = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const params = {
        search: searchTerm || undefined,
        group_type: selectedType || undefined,
        privacy_level: selectedPrivacy || undefined,
        my_groups: activeTab === 'my-groups',
        limit: 50
      }
      
      const response = await groupsAPI.getGroups(params)
      setGroups(response.results)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load groups')
      console.error('Error loading groups:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle join group
  const handleJoinGroup = async (groupId: string) => {
    try {
      await groupsAPI.joinGroup(groupId)
      loadGroups()
    } catch (err: any) {
      console.error('Error joining group:', err)
      alert(err.response?.data?.message || 'Failed to join group')
    }
  }

  // Handle leave group
  const handleLeaveGroup = async (groupId: string) => {
    if (!confirm('Are you sure you want to leave this group?')) return
    
    try {
      await groupsAPI.leaveGroup(groupId)
      loadGroups()
    } catch (err: any) {
      console.error('Error leaving group:', err)
      alert(err.response?.data?.message || 'Failed to leave group')
    }
  }

  useEffect(() => {
    loadGroups()
  }, [activeTab, searchTerm, selectedType, selectedPrivacy])

  return (
    <div className="min-h-screen bg-background">
      {/* Modern Header */}
      <header className="sticky top-0 z-40 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="content-container">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-2xl font-bold">
                <span className="gradient-text">Coptic Social</span>
              </Link>
              <div className="h-6 w-px bg-border"></div>
              <h1 className="text-xl font-semibold text-foreground">Community Groups</h1>
            </div>
            
            <Link href="/groups/create">
              <Button variant="spiritual" className="shadow-spiritual-500/20">
                Create Group
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="content-container section-spacing">
        {/* Modern Tab Navigation */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex space-x-1 bg-muted rounded-lg p-1">
            {(['discover', 'my-groups'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  "px-4 py-2 text-sm font-medium rounded-md transition-all duration-200",
                  activeTab === tab
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {tab === 'discover' ? 'Discover Groups' : 'My Groups'}
              </button>
            ))}
          </div>
        </div>

        {/* Modern Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Input
            placeholder="Search groups..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="col-span-1 md:col-span-1"
          />
          
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option value="">All Types</option>
            <option value="ministry">Ministry</option>
            <option value="committee">Committee</option>
            <option value="study">Study</option>
            <option value="prayer">Prayer</option>
            <option value="service">Service</option>
            <option value="social">Social</option>
            <option value="age_based">Age Based</option>
            <option value="interest">Interest</option>
          </select>
          
          <select
            value={selectedPrivacy}
            onChange={(e) => setSelectedPrivacy(e.target.value)}
            className="h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option value="">All Privacy Levels</option>
            <option value="public">Public</option>
            <option value="parish_only">Parish Only</option>
            <option value="private">Private</option>
            <option value="invite_only">Invite Only</option>
          </select>
        </div>

        {/* Groups Grid */}
        {loading ? (
          <div className="grid grid-auto-fit gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="overflow-hidden">
                <div className="h-48 bg-muted loading-shimmer"></div>
                <CardHeader>
                  <div className="h-4 bg-muted rounded loading-shimmer mb-2"></div>
                  <div className="h-3 bg-muted rounded loading-shimmer w-2/3"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-3 bg-muted rounded loading-shimmer"></div>
                    <div className="h-3 bg-muted rounded loading-shimmer w-3/4"></div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={loadGroups}>Try Again</Button>
          </div>
        ) : groups.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🏛️</div>
            <h3 className="text-lg font-semibold mb-2">No groups found</h3>
            <p className="text-muted-foreground mb-6">
              {activeTab === 'my-groups' 
                ? "You haven't joined any groups yet." 
                : "No groups match your current filters."}
            </p>
            {activeTab === 'discover' && (
              <Button onClick={() => {
                setSearchTerm('')
                setSelectedType('')
                setSelectedPrivacy('')
              }}>
                Clear Filters
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-auto-fit gap-6">
            {groups.map((group) => (
              <ModernGroupCard
                key={group.id}
                group={group}
                userMembership={group.user_membership || null}
                onJoin={handleJoinGroup}
                onLeave={handleLeaveGroup}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
} 