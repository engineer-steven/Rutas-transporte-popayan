import { OSM_POPAYAN_NEIGHBORHOODS } from './popayanPlaces.js'

export const POPAYAN_LOCATIONS = [
  'Centro',
  'Parque Caldas',
  'Terminal de Transporte',
  'Universidad del Cauca',
  'Hospital San José',
  'Centro Comercial Campanario',
  'La Paz',
  'Cajete',
  'El Morro',
  'Bello Horizonte',
  ...OSM_POPAYAN_NEIGHBORHOODS.map(([name]) => name),
]

export const PASSENGER_PLACE_DESCRIPTIONS = {
  'Parque Caldas': 'plaza principal centro histórico',
  'Terminal de Transporte': 'terminal de buses estación',
  'Universidad del Cauca': 'universidad sede central',
  'Centro Comercial Campanario': 'centro comercial tiendas',
}

export const PASSENGER_ROUTES = [
  {
    id: 'r1',
    code: 'R1',
    name: 'Ruta R1',
    company: 'Translibertad',
    via: 'Por Av. Bolívar',
    duration: 18,
    walkingMinutes: 5,
    transfers: 0,
    color: '#0877df',
    stops: [
      'Terminal de Transporte',
      'El Modelo',
      'El Centro',
      'Centro',
      'Parque Caldas',
      'Caldas',
      'Universidad del Cauca',
      'Hospital San José',
      'Centro Comercial Campanario',
      'Aida Lucía',
      'Galicia',
      'Las Acacias',
      'La Violeta',
      'Villa Alicia',
      'Ciudad Jardín',
    ],
  },
  {
    id: 'r2',
    code: 'R2',
    name: 'Ruta R2',
    company: 'Transpubenza',
    via: 'Por carrera 6',
    duration: 22,
    walkingMinutes: 4,
    transfers: 0,
    color: '#159b8a',
    stops: [
      'Villa del Norte o La Paz',
      'Barrio Villa del Norte',
      'Barrio Los Robles',
      'Barrio San Eduardo',
      'Los Ángeles',
      'La Aldea',
      'La Primavera',
      'Barrio Aire de Paz',
      'Barrio Cerrito de la Paz',
      'Barrio Chamisales',
      'Popular',
      'Bello Horizonte',
      'Club Residencial Camino Viejo',
      'Barrio Conjunto Cerrado Villa Claudia',
      'Conjunto Cerrado El Rincón Coomeva',
      'Conjunto Residencial Río Verde',
      'Condominio Campoalegre',
      'Torres de Milano',
      'Valle Robledo',
      'Universidad del Cauca',
      'Centro',
      'Terminal de Transporte',
    ],
  },
  {
    id: 'r3',
    code: 'R3',
    name: 'Ruta R3',
    company: 'TransTambo',
    via: 'Por el centro histórico',
    duration: 25,
    walkingMinutes: 6,
    transfers: 0,
    color: '#ee684d',
    stops: [
      'Cajete',
      'Barrio Voces de Esperanza',
      'Lomas de Granada',
      'Villa de Occidente',
      'Barrio Atardecer de Occidente',
      'Barrio Rivera de Occidente',
      'Bosques de Occidente',
      'Los Álamos de Occidente',
      'Indianápolis',
      'Vegas del Cauca',
      'Villa Colombia',
      'La María Occidente',
      'Barrio Munich',
      'Los Lagos',
      'El Morro',
      'Parque Caldas',
      'Centro',
      'Hospital San José',
      'Centro Comercial Campanario',
    ],
  },
  {
    id: 'r4',
    code: 'R4',
    name: 'Ruta R4',
    company: 'Transpubenza',
    via: 'Por el norte de Popayán',
    duration: 20,
    walkingMinutes: 3,
    transfers: 0,
    color: '#08756a',
    stops: [
      'Recuerdo Sur',
      'Túnel Bajo',
      'Las Veraneras',
      'Barrio Platiado',
      'Barrio Solidaridad',
      'Solidaridad',
      'Los Comuneros',
      'Alfonso López',
      'La María Oriente',
      'Santa Mónica',
      'Los Sauces',
      'El Arenal',
      'Loma de Cartagena',
      'Moscopán',
      'Centro',
      'Hospital San José',
      'Terminal de Transporte',
    ],
  },
  {
    id: 'r5',
    code: 'R5',
    name: 'Ruta R5',
    company: 'Translibertad',
    via: 'Por Av. Panamericana',
    duration: 16,
    walkingMinutes: 7,
    transfers: 0,
    color: '#4b98e5',
    stops: [
      'Yanaconas',
      'El Portal del Encanto',
      'Colina Campestre',
      'Lomas de Pomona',
      'Vereda Pomona',
      'Portal de la Colina',
      'El Cadillal',
      'La Esmeralda',
      'Pandiguando',
      'Perpetuo Socorro',
      'El Libertador',
      'José María Obando',
      'Camilo Torres',
      'Canada',
      'El Edén',
      'El Mirador',
      'San José',
      'Junín',
      'Kennedy',
      'El Modelo',
      'El Centro',
      'Centro',
      'Universidad del Cauca',
      'Centro Comercial Campanario',
      'La Paz',
    ],
  },
]

export function buscarRutasLocales(origen, destino) {
  const normalizar = (valor) => valor.trim().toLocaleLowerCase('es')
  const start = normalizar(origen)
  const end = normalizar(destino)
  const rutasBidireccionales = PASSENGER_ROUTES.flatMap((route) => [
    route,
    { ...route, stops: [...route.stops].reverse() },
  ])
  const directas = rutasBidireccionales.filter((route) => {
    const startIndex = route.stops.findIndex((stop) => normalizar(stop) === start)
    const endIndex = route.stops.findIndex((stop) => normalizar(stop) === end)
    return startIndex >= 0 && endIndex > startIndex
  }).map((route) => {
    const startIndex = route.stops.findIndex((stop) => normalizar(stop) === start)
    const endIndex = route.stops.findIndex((stop) => normalizar(stop) === end)
    return {
      ...route,
      fullStops: route.stops,
      stops: route.stops.slice(startIndex, endIndex + 1),
      transfers: 0,
    }
  })

  if (directas.length) return directas

  const conexiones = []
  for (const first of rutasBidireccionales) {
    const startIndex = first.stops.findIndex((stop) => normalizar(stop) === start)
    if (startIndex < 0) continue

    for (const second of rutasBidireccionales) {
      if (first.id === second.id) continue
      const endIndex = second.stops.findIndex((stop) => normalizar(stop) === end)
      if (endIndex < 1) continue

      const interchange = first.stops
        .slice(startIndex + 1)
        .find((stop) => second.stops.indexOf(stop) >= 0 && second.stops.indexOf(stop) < endIndex)
      if (!interchange) continue

      conexiones.push({
        ...first,
        id: `${first.id}-${second.id}`,
        code: `${first.code} + ${second.code}`,
        name: `${first.name} + ${second.name}`,
        company: `${first.company} · ${second.company}`,
        duration: first.duration + second.duration + 8,
        walkingMinutes: first.walkingMinutes,
        transfers: 1,
        interchange,
        stops: [
          ...first.stops.slice(startIndex, first.stops.indexOf(interchange) + 1),
          ...second.stops.slice(second.stops.indexOf(interchange) + 1, endIndex + 1),
        ],
        segmentRoutes: [
          {
            ...first,
            fullStops: first.stops,
            stops: first.stops.slice(startIndex, first.stops.indexOf(interchange) + 1),
          },
          {
            ...second,
            fullStops: second.stops,
            stops: second.stops.slice(second.stops.indexOf(interchange), endIndex + 1),
          },
        ],
      })
    }
  }

  return conexiones.slice(0, 3)
}
