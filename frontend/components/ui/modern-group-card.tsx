import React from 'react'
import Link from 'next/link'
import { Card, CardContent, CardFooter, CardHeader } from './card'
import { Button } from './button'
import { Badge } from './badge'
import { Group } from '../../lib/api'

// Group type icons mapping
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

export function ModernGroupCard({ 
  group, 
  userMembership, 
  onJoin, 
  onLeave, 
  isLoading = false 
}: ModernGroupCardProps) {
  const isMember = !!userMembership
  const canJoin = !isMember && (group.privacy_level === 'public' || group.privacy_level === 'parish_only')

  return (
    <Card className="group overflow-hidden hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
      {group.cover_image && (
        <div className="relative h-40 overflow-hidden">
          <img 
            src={group.cover_image} 
            alt={group.name}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
          
          {/* Privacy badge overlay */}
          <div className="absolute top-3 right-3">
            <Badge variant={group.privacy_level as any} className="backdrop-blur-sm bg-white/90">
              {group.privacy_level.replace('_', ' ')}
            </Badge>
          </div>
        </div>
      )}
      
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-2xl bg-gradient-to-br from-coptic-100 to-byzantine-100 p-2 rounded-lg">
              {GROUP_TYPE_ICONS[group.group_type]}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg leading-tight">
                {group.name}
              </h3>
              <p className="text-sm text-gray-600 capitalize font-medium">
                {group.group_type.replace('_', ' ')}
              </p>
            </div>
          </div>
          
          {isMember && (
            <Badge variant={userMembership.role as any}>
              {userMembership.role}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="pb-4">
        <p className="text-gray-600 text-sm leading-relaxed line-clamp-3 mb-4">
          {group.description}
        </p>

        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4 text-gray-500">
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-coptic-400 rounded-full"></span>
              <span>{group.member_count} members</span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="w-2 h-2 bg-byzantine-400 rounded-full"></span>
              <span>{group.post_count} posts</span>
            </div>
          </div>
          <span className="text-xs text-gray-400 font-medium">
            {group.parish.name}
          </span>
        </div>
      </CardContent>

      <CardFooter className="flex items-center justify-between pt-4 border-t border-gray-100">
        <Link 
          href={`/groups/${group.id}`}
          className="flex items-center space-x-1 text-coptic-600 hover:text-coptic-700 font-medium text-sm transition-colors"
        >
          <span>View Details</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
        
        <div className="flex space-x-2">
          {isMember ? (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onLeave(group.id)}
              disabled={isLoading}
              className="hover:bg-red-50 hover:text-red-600 hover:border-red-200"
            >
              Leave
            </Button>
          ) : canJoin ? (
            <Button
              variant="default"
              size="sm"
              onClick={() => onJoin(group.id)}
              disabled={isLoading}
              className="shadow-coptic-600/20 hover:shadow-coptic-600/30"
            >
              Join Group
            </Button>
          ) : (
            <Badge variant="outline" className="px-3 py-1">
              {group.privacy_level === 'private' ? 'Private' : 'Invite Only'}
            </Badge>
          )}
        </div>
      </CardFooter>
    </Card>
  )
} 