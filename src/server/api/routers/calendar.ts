import { z } from 'zod'
import { createTRPCRouter, protectedProcedure } from '~/server/api/trpc'
import { GoogleCalendarService, type CalendarEvent } from '~/server/services/google-calendar-service'

const handleCalendarError = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    throw new Error(error.message || fallback)
  }
  throw new Error(fallback)
}

export const calendarRouter = createTRPCRouter({
  /**
   * List calendar events
   */
  listEvents: protectedProcedure
    .input(
      z.object({
        timeMin: z.date().optional(),
        timeMax: z.date().optional(),
        maxResults: z.number().optional(),
      })
    )
    .query(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        const events = await calendarService.listEvents({
          timeMin: input.timeMin,
          timeMax: input.timeMax,
          maxResults: input.maxResults,
        })

        return events
      } catch (error) {
        handleCalendarError(error, '無法取得行事曆事件')
      }
    }),

  /**
   * Get a specific event
   */
  getEvent: protectedProcedure
    .input(
      z.object({
        eventId: z.string(),
      })
    )
    .query(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        return await calendarService.getEvent(input.eventId)
      } catch (error) {
        handleCalendarError(error, '無法取得事件詳情')
      }
    }),

  /**
   * Create a new event
   */
  createEvent: protectedProcedure
    .input(
      z.object({
        summary: z.string(),
        description: z.string().optional(),
        startDateTime: z.date(),
        endDateTime: z.date(),
        timeZone: z.string().optional().default('Asia/Taipei'),
        reminders: z
          .object({
            useDefault: z.boolean(),
            overrides: z
              .array(
                z.object({
                  method: z.enum(['email', 'popup']),
                  minutes: z.number(),
                })
              )
              .optional(),
          })
          .optional(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        const event = await calendarService.createEvent({
          summary: input.summary,
          description: input.description,
          start: {
            dateTime: input.startDateTime.toISOString(),
            timeZone: input.timeZone,
          },
          end: {
            dateTime: input.endDateTime.toISOString(),
            timeZone: input.timeZone,
          },
          reminders: input.reminders,
        })

        return event
      } catch (error) {
        handleCalendarError(error, '無法建立事件')
      }
    }),

  /**
   * Update an event
   */
  updateEvent: protectedProcedure
    .input(
      z.object({
        eventId: z.string(),
        summary: z.string().optional(),
        description: z.string().optional(),
        startDateTime: z.date().optional(),
        endDateTime: z.date().optional(),
        timeZone: z.string().optional().default('Asia/Taipei'),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        const updateData: Partial<CalendarEvent> = {}

        if (input.summary) updateData.summary = input.summary
        if (input.description) updateData.description = input.description
        if (input.startDateTime) {
          updateData.start = {
            dateTime: input.startDateTime.toISOString(),
            timeZone: input.timeZone,
          }
        }
        if (input.endDateTime) {
          updateData.end = {
            dateTime: input.endDateTime.toISOString(),
            timeZone: input.timeZone,
          }
        }

        const event = await calendarService.updateEvent(input.eventId, updateData)

        return event
      } catch (error) {
        handleCalendarError(error, '無法更新事件')
      }
    }),

  /**
   * Delete an event
   */
  deleteEvent: protectedProcedure
    .input(
      z.object({
        eventId: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        await calendarService.deleteEvent(input.eventId)
        return { success: true }
      } catch (error) {
        handleCalendarError(error, '無法刪除事件')
      }
    }),

  /**
   * Sync assignment to calendar
   */
  syncAssignment: protectedProcedure
    .input(
      z.object({
        assignmentId: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        await calendarService.syncAssignment(input.assignmentId)
        return { success: true, message: '已同步到 Google Calendar' }
      } catch (error) {
        handleCalendarError(error, '無法同步作業到行事曆')
      }
    }),

  /**
   * Remove assignment from calendar
   */
  unsyncAssignment: protectedProcedure
    .input(
      z.object({
        assignmentId: z.string(),
      })
    )
    .mutation(async ({ ctx, input }) => {
      const calendarService = new GoogleCalendarService(ctx.session.user.id)

      try {
        await calendarService.unsyncAssignment(input.assignmentId)
        return { success: true, message: '已從行事曆移除' }
      } catch (error) {
        handleCalendarError(error, '無法從行事曆移除')
      }
    }),

  /**
   * List available calendars
   */
  listCalendars: protectedProcedure.query(async ({ ctx }) => {
    const calendarService = new GoogleCalendarService(ctx.session.user.id)

    try {
      return await calendarService.listCalendars()
    } catch (error) {
      handleCalendarError(error, '無法取得行事曆列表')
    }
  }),

  /**
   * Get calendar connection status
   */
  getConnectionStatus: protectedProcedure.query(async ({ ctx }) => {
    const account = await ctx.db.account.findFirst({
      where: {
        userId: ctx.session.user.id,
        provider: 'google',
      },
    })

    return {
      connected: !!account && !!account.access_token,
      hasRefreshToken: !!account?.refresh_token,
    }
  }),
})
