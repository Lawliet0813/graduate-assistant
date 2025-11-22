// Middleware is disabled for database session strategy
// Authentication is handled at page level
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  return NextResponse.next()
}

export const config = {
  matcher: [], // Disabled - using page-level auth
}
