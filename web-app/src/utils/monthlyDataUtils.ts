/**
 * Utility functions for working with optimized monthly facility data
 */

export interface OptimizedFacility {
  i: number;    // id
  n: string;    // name
  lat: number;  // latitude
  lng: number;  // longitude
  a: string;    // address
}

export interface OptimizedMonthlyData {
  meta: {
    v: number;           // version
    t: string;           // timestamp
    f: number;           // facility count
    m: string[];         // available months
    l: string;           // latest month
    d: string;           // description
  };
  facilities: OptimizedFacility[];
  data: Record<number, number[]>; // facility_id -> population array
}

export interface MonthlyFacilityData {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  address: string;
  population_count: number;
}

/**
 * Get facility data for a specific month from optimized data
 */
export function getFacilitiesForMonth(
  data: OptimizedMonthlyData,
  monthYear: string
): MonthlyFacilityData[] {
  const monthIndex = data.meta.m.indexOf(monthYear);
  if (monthIndex === -1) {
    console.warn(`Month ${monthYear} not found in available months`);
    return [];
  }

  const facilities: MonthlyFacilityData[] = [];
  
  for (const facility of data.facilities) {
    const populationData = data.data[facility.i];
    if (populationData && populationData[monthIndex] > 0) {
      facilities.push({
        id: facility.i,
        name: facility.n,
        latitude: facility.lat,
        longitude: facility.lng,
        address: facility.a,
        population_count: populationData[monthIndex]
      });
    }
  }

  return facilities;
}

/**
 * Get all available months from optimized data
 */
export function getAvailableMonths(data: OptimizedMonthlyData): string[] {
  return data.meta.m;
}

/**
 * Get the latest available month
 */
export function getLatestMonth(data: OptimizedMonthlyData): string {
  return data.meta.l;
}

/**
 * Get facility count for a specific month
 */
export function getFacilityCountForMonth(
  data: OptimizedMonthlyData,
  monthYear: string
): number {
  return getFacilitiesForMonth(data, monthYear).length;
}

/**
 * Get population trend for a facility across all months
 */
export function getFacilityTrend(
  data: OptimizedMonthlyData,
  facilityId: number
): { month: string; population: number }[] {
  const populationData = data.data[facilityId];
  if (!populationData) {
    return [];
  }

  return data.meta.m.map((month, index) => ({
    month,
    population: populationData[index] || 0
  }));
}

/**
 * Find facilities with population changes between two months
 */
export function getFacilitiesWithChanges(
  data: OptimizedMonthlyData,
  fromMonth: string,
  toMonth: string
): {
  facility: OptimizedFacility;
  fromPopulation: number;
  toPopulation: number;
  change: number;
  changePercent: number;
}[] {
  const fromIndex = data.meta.m.indexOf(fromMonth);
  const toIndex = data.meta.m.indexOf(toMonth);
  
  if (fromIndex === -1 || toIndex === -1) {
    return [];
  }

  const changes: {
    facility: OptimizedFacility;
    fromPopulation: number;
    toPopulation: number;
    change: number;
    changePercent: number;
  }[] = [];

  for (const facility of data.facilities) {
    const populationData = data.data[facility.i];
    if (populationData) {
      const fromPopulation = populationData[fromIndex] || 0;
      const toPopulation = populationData[toIndex] || 0;
      
      if (fromPopulation !== toPopulation) {
        const change = toPopulation - fromPopulation;
        const changePercent = fromPopulation > 0 ? (change / fromPopulation) * 100 : 0;
        
        changes.push({
          facility,
          fromPopulation,
          toPopulation,
          change,
          changePercent
        });
      }
    }
  }

  return changes.sort((a, b) => Math.abs(b.change) - Math.abs(a.change));
}

/**
 * Format month-year string for display
 */
export function formatMonthYear(monthYear: string): string {
  const [year, month] = monthYear.split('-');
  const date = new Date(parseInt(year), parseInt(month) - 1);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long' 
  });
}

/**
 * Get month options for dropdown (formatted for display)
 */
export function getMonthOptions(data: OptimizedMonthlyData): { value: string; label: string }[] {
  return data.meta.m.map(month => ({
    value: month,
    label: formatMonthYear(month)
  })).reverse(); // Most recent first
}

/**
 * Get top facilities by population for a specific month
 */
export function getTopFacilitiesForMonth(
  data: OptimizedMonthlyData,
  monthYear: string,
  limit: number = 10
): MonthlyFacilityData[] {
  const facilities = getFacilitiesForMonth(data, monthYear);
  return facilities
    .sort((a, b) => b.population_count - a.population_count)
    .slice(0, limit);
}

/**
 * Get total population for a specific month
 */
export function getTotalPopulationForMonth(
  data: OptimizedMonthlyData,
  monthYear: string
): number {
  const facilities = getFacilitiesForMonth(data, monthYear);
  return facilities.reduce((total, facility) => total + facility.population_count, 0);
}

/**
 * Validate that optimized data structure is correct
 */
export function validateOptimizedData(data: any): data is OptimizedMonthlyData {
  return (
    data &&
    data.meta &&
    typeof data.meta.v === 'number' &&
    typeof data.meta.t === 'string' &&
    typeof data.meta.f === 'number' &&
    Array.isArray(data.meta.m) &&
    typeof data.meta.l === 'string' &&
    Array.isArray(data.facilities) &&
    typeof data.data === 'object'
  );
}
