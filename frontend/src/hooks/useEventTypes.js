import { useState, useEffect, useCallback } from 'react';
import { getEventTypes } from '../api/client';

/**
 * Fetches all EventTypeDefinition records once from GET /event-types.
 * Cached in local state for the lifetime of the component that mounts it.
 * The event type list changes rarely (seeded presets), so a single fetch is fine.
 *
 * Returns: { eventTypes: [], isLoading: bool, error: string | null }
 */
function useEventTypes() {
  const [eventTypes, setEventTypes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEventTypes = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await getEventTypes();
      setEventTypes(data);
    } catch {
      setError('Failed to load event types. Please check that the backend is running.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEventTypes();
  }, [fetchEventTypes]);

  return { eventTypes, isLoading, error };
}

export default useEventTypes;
