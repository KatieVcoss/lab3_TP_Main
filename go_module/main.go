package main

import (
	"encoding/csv"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

type InflationRecord struct {
	Year      int     `json:"year"`
	Inflation float64 `json:"inflation"`
}

type ForecastRecord struct {
	Year      int     `json:"year"`
	Inflation float64 `json:"inflation"`
}

type Result struct {
	Records        []InflationRecord `json:"records"`
	Forecast       []ForecastRecord  `json:"forecast"`
	BasePrice      float64           `json:"base_price"`
	EstimatedPrice float64           `json:"estimated_price"`
	Window         int               `json:"window"`
	Years          int               `json:"years"`
}

type InflationService interface {
	LoadCSV(path string) ([]InflationRecord, error)
	Forecast(records []InflationRecord, years int, window int) ([]ForecastRecord, error)
	EstimatePrice(basePrice float64, forecast []ForecastRecord) float64
}

type InflationCalculator struct{}

func main() {
	filePath := flag.String("file", "", "Path to CSV file with inflation data")
	years := flag.Int("years", 3, "Number of years to forecast")
	window := flag.Int("window", 3, "Moving average window")
	price := flag.Float64("price", 1000.0, "Base product/service price")

	flag.Parse()

	service := InflationCalculator{}

	records, err := service.LoadCSV(*filePath)
	if err != nil {
		printErrorAndExit(err)
	}

	forecast, err := service.Forecast(records, *years, *window)
	if err != nil {
		printErrorAndExit(err)
	}

	estimatedPrice := service.EstimatePrice(*price, forecast)

	result := Result{
		Records:        records,
		Forecast:       forecast,
		BasePrice:      *price,
		EstimatedPrice: estimatedPrice,
		Window:         *window,
		Years:          *years,
	}

	jsonBytes, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		printErrorAndExit(err)
	}

	fmt.Println(string(jsonBytes))
}

func (InflationCalculator) LoadCSV(path string) ([]InflationRecord, error) {
	if path == "" {
		return nil, errors.New("не указан путь к CSV-файлу")
	}

	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("не удалось открыть файл: %w", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.FieldsPerRecord = -1

	rows, err := reader.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("не удалось прочитать CSV: %w", err)
	}

	if len(rows) < 2 {
		return nil, errors.New("в CSV должно быть минимум 2 строки: заголовок и данные")
	}

	records := make([]InflationRecord, 0)

	for i, row := range rows {
		if i == 0 {
			continue
		}

		if len(row) < 2 {
			continue
		}

		yearText := strings.TrimSpace(row[0])
		inflationText := strings.TrimSpace(row[1])
		inflationText = strings.ReplaceAll(inflationText, ",", ".")

		year, err := strconv.Atoi(yearText)
		if err != nil {
			return nil, fmt.Errorf("ошибка года в строке %d: %w", i+1, err)
		}

		inflation, err := strconv.ParseFloat(inflationText, 64)
		if err != nil {
			return nil, fmt.Errorf("ошибка инфляции в строке %d: %w", i+1, err)
		}

		records = append(records, InflationRecord{
			Year:      year,
			Inflation: inflation,
		})
	}

	if len(records) == 0 {
		return nil, errors.New("не найдено данных об инфляции")
	}

	sort.Slice(records, func(i, j int) bool {
		return records[i].Year < records[j].Year
	})

	return records, nil
}

func (InflationCalculator) Forecast(records []InflationRecord, years int, window int) ([]ForecastRecord, error) {
	if years <= 0 {
		return nil, errors.New("количество лет прогноза должно быть больше 0")
	}

	if window <= 0 {
		return nil, errors.New("окно скользящей средней должно быть больше 0")
	}

	if len(records) < window {
		return nil, errors.New("данных меньше, чем размер окна скользящей средней")
	}

	values := make([]float64, 0)

	for _, record := range records {
		values = append(values, record.Inflation)
	}

	lastYear := records[len(records)-1].Year
	forecast := make([]ForecastRecord, 0)

	for i := 1; i <= years; i++ {
		average := averageLast(values, window)
		values = append(values, average)

		forecast = append(forecast, ForecastRecord{
			Year:      lastYear + i,
			Inflation: round2(average),
		})
	}

	return forecast, nil
}

func (InflationCalculator) EstimatePrice(basePrice float64, forecast []ForecastRecord) float64 {
	price := basePrice

	for _, item := range forecast {
		price = price * (1 + item.Inflation/100.0)
	}

	return round2(price)
}

func averageLast(values []float64, window int) float64 {
	start := len(values) - window
	sum := 0.0

	for i := start; i < len(values); i++ {
		sum += values[i]
	}

	return sum / float64(window)
}

func round2(value float64) float64 {
	return float64(int(value*100+0.5)) / 100
}

func printErrorAndExit(err error) {
	errorResult := map[string]string{
		"error": err.Error(),
	}

	jsonBytes, _ := json.Marshal(errorResult)
	fmt.Println(string(jsonBytes))
	os.Exit(1)
}
