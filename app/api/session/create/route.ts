import { type NextRequest, NextResponse } from "next/server"

// Simple in-memory session storage for demo
const sessions = new Map<string, { id: string; userType: string; createdAt: Date }>()

export async function POST(request: NextRequest) {
  try {
    const { user_type } = await request.json()

    // Generate a simple session ID
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // Store session
    sessions.set(sessionId, {
      id: sessionId,
      userType: user_type,
      createdAt: new Date(),
    })

    return NextResponse.json({
      session_id: sessionId,
      status: "success",
    })
  } catch (error) {
    console.error("Session creation error:", error)
    return NextResponse.json({ error: "Failed to create session" }, { status: 500 })
  }
}
