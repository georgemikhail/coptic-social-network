
# 📘 Product Requirements Document (PRD)

## 1. Overview

### Purpose:
To define the technical and functional specifications for building a **global social networking platform** for Coptic Orthodox Christians.

### Goals:
- Centralize digital interaction among Coptic Orthodox faithful worldwide
- Connect users with their local parish and diocese
- Provide tools for communication, commerce, and community-building
- Enable robust administrative control and scalability

---

## 2. Key Personas

| Role | Description |
|------|-------------|
| General User | Registers, joins a parish, interacts with content |
| Parish Admin | Manages parish page, content, donations |
| Diocese Admin | Oversees parishes in the diocese |
| Super Admin | Full platform control |
| Visitor | Public non-registered viewer (optional) |

---

## 3. Features & Functional Requirements

### A. Authentication & Profile
- Email/password or OAuth (Google/Facebook)
- Must select one parish
- Custom profile fields (gender, LinkedIn, etc.)
- Super Admin can define profile schema

### B. Posts & Feeds
- Support text, photos, video, audio, files
- Parish and global feed
- Reactions, comments, tagging

### C. Parish Pages
- Bio, clergy, service schedule, WhatsApp integration
- Livestream, multimedia, events
- “Donate” with campaign goals

### D. Diocese Pages
- Oversees parishes, bishop info, events

### E. Groups & Communities
- Interest pages, department pages
- Created by Super Admin or users (approval required)
- Posts, files, events

### F. Jobs & Marketplace
- User/parish job posts and product listings
- Inquiry or payment integration (Stripe, PayPal)

### G. Calendar Sync
- Export ICS or Google Calendar API
- RSVP to events

### H. WhatsApp Integration
- Join button and message stream (read-only)
- Requires WhatsApp Business API or webhook service

### I. Permissions
- Role matrix for Super Admin, Diocese Admin, Parish Admin, Users
- Custom visibility controls

---

## 4. Non-Functional Requirements

- Mobile App Support (React Native)
- Security (RBAC, 2FA, GDPR)
- Cloud media storage (S3/Firebase)
- Performance and offline access

---

## 5. KPIs

- Monthly active users
- Parish onboarding count
- Engagement per parish
- Donations and product sales
