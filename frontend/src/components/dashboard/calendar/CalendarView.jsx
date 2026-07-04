import React, { useState, useMemo, useEffect } from 'react';
import CalendarHeader from './CalendarHeader';
import CalendarGrid from './CalendarGrid';
import CalendarFilters from './CalendarFilters';
import DayDetailsPanel from './DayDetailsPanel';
import CalendarLegend from './CalendarLegend';
import { generateMonthGrid } from './CalendarUtils';

export default function CalendarView({ 
  planData, 
  semester, 
  semesterEvents, 
  subjectMap 
}) {
  // Navigation State
  const [currentDate, setCurrentDate] = useState(() => {
    // Default to today, or semester start if today is before semester
    const today = new Date();
    const start = new Date(semester.start_date);
    if (today < start) return start;
    return today;
  });

  // Details Panel State
  const [selectedDay, setSelectedDay] = useState(null);

  // Filter State
  const [activeFilters, setActiveFilters] = useState({
    attend: false,
    skip: false,
    holiday: false,
    event: false
  });

  // Calculate Semester Boundaries
  const semesterStart = useMemo(() => new Date(semester.start_date), [semester.start_date]);
  const semesterEnd = useMemo(() => new Date(semester.end_date), [semester.end_date]);

  // Derived Grid
  const monthGrid = useMemo(() => {
    return generateMonthGrid(currentDate.getFullYear(), currentDate.getMonth());
  }, [currentDate]);

  // Fast map for plan days (date string -> planDay object)
  const planDaysMap = useMemo(() => {
    const map = {};
    if (planData && planData.days) {
      planData.days.forEach(d => {
        map[d.date] = d;
      });
    }
    return map;
  }, [planData]);

  // Navigation Handlers
  const handlePrevMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  const handleToday = () => {
    const today = new Date();
    // If today is outside semester, jump to start date
    if (today < semesterStart || today > semesterEnd) {
      setCurrentDate(new Date(semesterStart.getFullYear(), semesterStart.getMonth(), 1));
    } else {
      setCurrentDate(new Date(today.getFullYear(), today.getMonth(), 1));
    }
  };

  const toggleFilter = (filterId) => {
    setActiveFilters(prev => ({ ...prev, [filterId]: !prev[filterId] }));
  };

  const handleDayClick = (dateObj, planDay, dayEvents) => {
    setSelectedDay({ dateObj, planDay, dayEvents });
  };

  const closePanel = () => {
    setSelectedDay(null);
  };

  // Check boundaries to disable Prev/Next buttons
  const canGoPrev = useMemo(() => {
    const firstDayOfTargetMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1);
    const lastDayOfTargetMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0);
    // If the entire target month is before the semester start month, disable.
    // Allow if any part of the month overlaps the semester month.
    return lastDayOfTargetMonth >= new Date(semesterStart.getFullYear(), semesterStart.getMonth(), 1);
  }, [currentDate, semesterStart]);

  const canGoNext = useMemo(() => {
    const firstDayOfTargetMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1);
    // If the entire target month is after the semester end month, disable.
    return firstDayOfTargetMonth <= new Date(semesterEnd.getFullYear(), semesterEnd.getMonth() + 1, 0);
  }, [currentDate, semesterEnd]);

  return (
    <div className={`relative transition-all duration-300 ${selectedDay ? 'md:pr-[400px] lg:pr-[450px]' : ''}`}>
      
      {/* Main Calendar Area */}
      <div className="max-w-4xl mx-auto w-full">
        <CalendarHeader 
          currentDate={currentDate}
          onPrevMonth={handlePrevMonth}
          onNextMonth={handleNextMonth}
          onToday={handleToday}
          canGoPrev={canGoPrev}
          canGoNext={canGoNext}
        />
        <CalendarFilters 
          activeFilters={activeFilters}
          toggleFilter={toggleFilter}
        />
        <CalendarGrid 
          monthGrid={monthGrid}
          planDaysMap={planDaysMap}
          semesterEvents={semesterEvents}
          semesterStart={semesterStart}
          semesterEnd={semesterEnd}
          activeFilters={activeFilters}
          onDayClick={handleDayClick}
        />
        <CalendarLegend />
      </div>

      {/* Details Panel */}
      {selectedDay && (
        <DayDetailsPanel 
          dateObj={selectedDay.dateObj}
          planDay={selectedDay.planDay}
          dayEvents={selectedDay.dayEvents}
          subjectMap={subjectMap}
          onClose={closePanel}
        />
      )}
    </div>
  );
}
