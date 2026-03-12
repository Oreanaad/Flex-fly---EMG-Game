void setup() {
  Serial.begin(9600);
}

void loop() {
  long sumaA = 0;
  long sumaB = 0;
  int muestras = 20; 

  // Tomamos lecturas de ambos canales para promediar
  for(int i = 0; i < muestras; i++) {
    sumaA += analogRead(A0);
    sumaB += analogRead(A1);
    delay(2); 
  }
  
  int promedioA = sumaA / muestras;
  int promedioB = sumaB / muestras;

  // Mapeo para ambos (0-1023 -> 1000-0)
  int valorMapeadoA = map(promedioA, 0, 1023, 1000, 0);
  int valorMapeadoB = map(promedioB, 0, 1023, 1000, 0);

  // ZONA MUERTA AGRESIVA para ambos
  if (valorMapeadoA < 150) valorMapeadoA = 0;
  if (valorMapeadoB < 150) valorMapeadoB = 0;

  // Enviamos al juego en el formato: "A,B"
  Serial.print(valorMapeadoA);
  Serial.print(",");
  Serial.println(valorMapeadoB);
}