import React, { useState, useEffect } from 'react'
import { createTrip, getTripStatus, getTripResult } from '@/lib/api'
import type { TripStatusResponse, TripResult } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import {
  CheckCircle2,
  Loader2,
  AlertCircle,
  Car,
  ShieldCheck,
  Activity,
  MapPin,
} from 'lucide-react'

const STEPS = [
  { id: 'PENDING', label: 'Data Ingested', icon: MapPin },
  { id: 'PROCESSING', label: 'Analyzing Telemetry', icon: Activity },
  { id: 'COMPLETED', label: 'Analysis Complete', icon: ShieldCheck },
]

export const Dashboard: React.FC = () => {
  const [activeTripId, setActiveTripId] = useState<string | null>(null)
  const [status, setStatus] = useState<TripStatusResponse | null>(null)
  const [result, setResult] = useState<TripResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleStartTrip = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await createTrip('DRIVER-001')
      setActiveTripId(data.trip_id)
    } catch (err) {
      setError('Failed to start trip simulation')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | undefined

    if (activeTripId && (!status || status.status !== 'COMPLETED')) {
      interval = setInterval(async () => {
        try {
          const statusData = await getTripStatus(activeTripId)
          setStatus(statusData)

          if (statusData.status === 'COMPLETED') {
            const resultData = await getTripResult(activeTripId)
            setResult(resultData)
            clearInterval(interval)
          }
        } catch (err) {
          console.error('Error polling status:', err)
        }
      }, 2000)
    }

    return () => clearInterval(interval)
  }, [activeTripId, status])

  const getStepStatus = (stepId: string) => {
    if (!status) return 'upcoming'
    const statusOrder = ['PENDING', 'PROCESSING', 'COMPLETED']
    const currentIndex = statusOrder.indexOf(status.status)
    const stepIndex = statusOrder.indexOf(stepId)

    if (status.status === 'FAILED') return 'failed'
    if (currentIndex > stepIndex) return 'completed'
    if (currentIndex === stepIndex) return 'current'
    return 'upcoming'
  }

  const getProgressValue = () => {
    if (!status) return 0
    switch (status.status) {
      case 'PENDING':
        return 33
      case 'PROCESSING':
        return 66
      case 'COMPLETED':
        return 100
      default:
        return 0
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">FleetFlow Dashboard</h1>
          <p className="text-muted-foreground">Real-time driver safety analysis pipeline.</p>
        </div>
        <Button onClick={handleStartTrip} disabled={loading || status?.status === 'PROCESSING'}>
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Car className="mr-2 h-4 w-4" />
          )}
          Start New Trip Simulation
        </Button>
      </div>

      {error && (
        <div className="bg-destructive/15 text-destructive flex items-center gap-2 rounded-lg p-4">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {activeTripId && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Trip Analysis Pipeline</span>
              <span className="text-muted-foreground font-mono text-sm">{activeTripId}</span>
            </CardTitle>
            <CardDescription>Tracking the lifecycle of your telemetry data.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="relative flex justify-between">
              {STEPS.map((step) => {
                const stepStatus = getStepStatus(step.id)
                const Icon = step.icon

                return (
                  <div key={step.id} className="bg-background z-10 flex flex-col items-center px-4">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors duration-500 ${
                        stepStatus === 'completed'
                          ? 'bg-primary border-primary text-primary-foreground'
                          : stepStatus === 'current'
                            ? 'border-primary text-primary animate-pulse'
                            : 'border-muted text-muted-foreground'
                      } `}
                    >
                      {stepStatus === 'completed' ? (
                        <CheckCircle2 className="h-6 w-6" />
                      ) : (
                        <Icon className="h-6 w-6" />
                      )}
                    </div>
                    <span
                      className={`mt-2 text-sm font-medium ${stepStatus === 'current' ? 'text-primary' : 'text-muted-foreground'}`}
                    >
                      {step.label}
                    </span>
                  </div>
                )
              })}
              <div className="bg-muted absolute top-5 right-0 left-0 z-0 h-0.5" />
              <div
                className="bg-primary absolute top-5 left-0 z-0 h-0.5 transition-all duration-500"
                style={{ width: `${getProgressValue()}%` }}
              />
            </div>

            <Progress value={getProgressValue()} className="h-2" />
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Safety Score</CardTitle>
              <ShieldCheck className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.safety_score.toFixed(1)}</div>
              <p className="text-muted-foreground text-xs">
                Risk Level:{' '}
                <span
                  className={`font-bold ${result.risk_level === 'Low' ? 'text-green-500' : result.risk_level === 'Medium' ? 'text-yellow-500' : 'text-red-500'}`}
                >
                  {result.risk_level}
                </span>
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Speeding Events</CardTitle>
              <Activity className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.speeding_count}</div>
              <p className="text-muted-foreground text-xs">
                Total distance: {result.total_distance.toFixed(2)} km
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Harsh Braking</CardTitle>
              <AlertCircle className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.harsh_braking_count}</div>
              <p className="text-muted-foreground text-xs">
                Avg Speed: {result.avg_speed.toFixed(1)} km/h
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Harsh Accel</CardTitle>
              <Activity className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.harsh_acceleration_count}</div>
              <p className="text-muted-foreground text-xs">Driver: {result.driver_id}</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
