//+------------------------------------------------------------------+
//| ExportXAU.mq5 - Exporta XAUUSD M3 a CSV                        |
//+------------------------------------------------------------------+
#property script_show_inputs

input int BarsToExport = 100000; // Cantidad de velas a exportar

void OnStart()
{
   string symbol    = "XAUUSD";
   ENUM_TIMEFRAMES tf = PERIOD_M3;

   // Cargar historial completo
   datetime from = 0;
   int loaded = CopyRates(symbol, tf, 0, BarsToExport, NULL);

   MqlRates rates[];
   int total = CopyRates(symbol, tf, 0, BarsToExport, rates);

   if(total <= 0) {
      Print("Error cargando datos: ", GetLastError());
      return;
   }

   // Crear archivo CSV en carpeta Files de MT5
   string filename = "XAUUSD_M3_export.csv";
   int handle = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_ANSI, ',');

   if(handle == INVALID_HANDLE) {
      Print("Error creando archivo: ", GetLastError());
      return;
   }

   // Encabezado
   FileWrite(handle, "time", "open", "high", "low", "close", "tick_volume");

   // Datos
   for(int i = total - 1; i >= 0; i--) {
      string dt = TimeToString(rates[i].time, TIME_DATE | TIME_MINUTES);
      FileWrite(handle,
         dt,
         DoubleToString(rates[i].open,  3),
         DoubleToString(rates[i].high,  3),
         DoubleToString(rates[i].low,   3),
         DoubleToString(rates[i].close, 3),
         IntegerToString(rates[i].tick_volume)
      );
   }

   FileClose(handle);
   Print("Exportado: ", total, " velas → ", filename);
   Alert("Listo! Exportadas ", total, " velas de XAUUSD M3.\nArchivo: ", filename);
}
