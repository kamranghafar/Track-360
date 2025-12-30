/**
 * Enhanced Charts Configuration
 * This file provides improved chart configurations for Chart.js to enhance
 * the UI/UX of all charts in the dashboard with a modern, professional look.
 */

// Define a consistent color palette for all charts with modern, professional colors
const chartColorPalette = {
    primary: [
        'rgba(67, 97, 238, 0.7)',  // Primary blue
        'rgba(72, 149, 239, 0.7)', // Light blue
        'rgba(76, 201, 240, 0.7)', // Cyan
        'rgba(46, 204, 113, 0.7)', // Green
        'rgba(155, 89, 182, 0.7)', // Purple
        'rgba(241, 196, 15, 0.7)', // Yellow
        'rgba(231, 76, 60, 0.7)',  // Red
        'rgba(52, 73, 94, 0.7)',   // Dark blue
        'rgba(26, 188, 156, 0.7)', // Teal
        'rgba(243, 156, 18, 0.7)'  // Orange
    ],
    borders: [
        'rgba(67, 97, 238, 1)',    // Primary blue
        'rgba(72, 149, 239, 1)',   // Light blue
        'rgba(76, 201, 240, 1)',   // Cyan
        'rgba(46, 204, 113, 1)',   // Green
        'rgba(155, 89, 182, 1)',   // Purple
        'rgba(241, 196, 15, 1)',   // Yellow
        'rgba(231, 76, 60, 1)',    // Red
        'rgba(52, 73, 94, 1)',     // Dark blue
        'rgba(26, 188, 156, 1)',   // Teal
        'rgba(243, 156, 18, 1)'    // Orange
    ],
    // Specific colors for different chart types with improved visual hierarchy
    pie: [
        'rgba(67, 97, 238, 0.85)',  // Primary blue
        'rgba(72, 149, 239, 0.85)', // Light blue
        'rgba(76, 201, 240, 0.85)', // Cyan
        'rgba(46, 204, 113, 0.85)', // Green
        'rgba(155, 89, 182, 0.85)'  // Purple
    ],
    bar: [
        'rgba(67, 97, 238, 0.75)',  // Primary blue
        'rgba(46, 204, 113, 0.75)', // Green
        'rgba(241, 196, 15, 0.75)', // Yellow
        'rgba(231, 76, 60, 0.75)',  // Red
        'rgba(155, 89, 182, 0.75)'  // Purple
    ],
    line: [
        'rgba(67, 97, 238, 0.5)',   // Primary blue
        'rgba(46, 204, 113, 0.5)',  // Green
        'rgba(241, 196, 15, 0.5)',  // Yellow
        'rgba(231, 76, 60, 0.5)',   // Red
        'rgba(155, 89, 182, 0.5)'   // Purple
    ],
    // Gradient backgrounds for more visually appealing charts
    gradients: {
        blue: {
            start: 'rgba(67, 97, 238, 0.8)',
            end: 'rgba(76, 201, 240, 0.3)'
        },
        green: {
            start: 'rgba(46, 204, 113, 0.8)',
            end: 'rgba(26, 188, 156, 0.3)'
        },
        purple: {
            start: 'rgba(155, 89, 182, 0.8)',
            end: 'rgba(142, 68, 173, 0.3)'
        }
    }
};

/**
 * Creates an enhanced chart with improved UI/UX features
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {string} chartType - The type of chart (pie, bar, line, etc.)
 * @param {Array} labels - Optional array of labels
 * @param {Array} data - Optional array of data values
 * @param {Array} backgroundColor - Optional array of background colors
 * @param {Array} borderColor - Optional array of border colors
 * @param {Object} customOptions - Optional custom chart options
 * @returns {Chart} The created Chart.js instance
 */
function createEnhancedChart(canvasId, chartType, labels, data, backgroundColor, borderColor, customOptions) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    // Parse data from data attributes if available
    let chartLabels = labels;
    let chartData = data;

    if (canvas.hasAttribute('data-labels') && canvas.hasAttribute('data-values')) {
        try {
            chartLabels = JSON.parse(canvas.getAttribute('data-labels'));
            chartData = JSON.parse(canvas.getAttribute('data-values'));
        } catch (e) {
            console.error('Error parsing chart data:', e);
            return null;
        }
    }

    // Select appropriate colors based on chart type
    let bgColors, borderColors;

    if (chartType === 'pie' || chartType === 'doughnut') {
        bgColors = backgroundColor || chartColorPalette.pie;
        borderColors = borderColor || chartColorPalette.borders;
    } else if (chartType === 'bar') {
        bgColors = backgroundColor || chartColorPalette.bar;
        borderColors = borderColor || chartColorPalette.borders;
    } else if (chartType === 'line') {
        bgColors = backgroundColor || chartColorPalette.line;
        borderColors = borderColor || chartColorPalette.borders;
    } else {
        bgColors = backgroundColor || chartColorPalette.primary;
        borderColors = borderColor || chartColorPalette.borders;
    }

    // Ensure we have enough colors for all data points
    while (bgColors.length < chartData.length) {
        bgColors = bgColors.concat(bgColors);
        borderColors = borderColors.concat(borderColors);
    }

    // Default options with enhanced UI/UX features for a modern, professional look
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1200,
            easing: 'easeOutQuart',
            delay: function(context) {
                // Stagger animations for multiple datasets
                return context.dataIndex * 50;
            }
        },
        plugins: {
            legend: {
                display: true,
                position: chartType === 'pie' || chartType === 'doughnut' ? 'right' : 'top',
                labels: {
                    boxWidth: 15,
                    padding: 15,
                    usePointStyle: true,
                    pointStyle: 'circle',
                    font: {
                        size: 12,
                        family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                    }
                }
            },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(33, 37, 41, 0.85)',
                titleFont: {
                    size: 14,
                    weight: 'bold',
                    family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                },
                bodyFont: {
                    size: 13,
                    family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                },
                padding: 12,
                cornerRadius: 6,
                displayColors: true,
                borderColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 1,
                caretSize: 8,
                caretPadding: 6,
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }

                        if (context.parsed.y !== undefined) {
                            label += context.parsed.y;
                        } else if (context.parsed !== undefined) {
                            label += context.parsed;
                        }

                        return label;
                    }
                },
                // Add animation to tooltips
                animation: {
                    duration: 150
                }
            },
            // Add subtle shadow to charts
            shadowPlugin: {
                beforeDraw: function(chart) {
                    if (chart.config.options.plugins.shadowPlugin.enabled) {
                        const ctx = chart.ctx;
                        ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
                        ctx.shadowBlur = 10;
                        ctx.shadowOffsetX = 0;
                        ctx.shadowOffsetY = 4;
                    }
                },
                enabled: true
            }
        },
        layout: {
            padding: {
                top: 15,
                right: 25,
                bottom: 15,
                left: 15
            }
        },
        // Improve interaction with charts
        interaction: {
            mode: 'index',
            intersect: false,
            includeInvisible: false
        }
    };

    // Adjust options based on chart type with enhanced visual appeal
    if (chartType === 'bar') {
        defaultOptions.scales = {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.03)',
                    drawBorder: false
                },
                border: {
                    dash: [4, 4]
                },
                ticks: {
                    precision: 0,
                    font: {
                        size: 11,
                        family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                    },
                    color: 'rgba(0, 0, 0, 0.6)'
                }
            },
            x: {
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    font: {
                        size: 11,
                        family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                    },
                    color: 'rgba(0, 0, 0, 0.6)'
                }
            }
        };

        // Enhanced hover effects for bar charts
        defaultOptions.plugins.tooltip.callbacks.label = function(context) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            // Format numbers with commas for thousands
            label += new Intl.NumberFormat().format(context.parsed.y);
            return label;
        };

        // Add bar thickness and border radius for modern look
        defaultOptions.elements = {
            bar: {
                borderRadius: 4,
                borderSkipped: false,
                // Add subtle hover effect
                hoverBackgroundColor: context => {
                    const color = context.dataset.backgroundColor[context.dataIndex];
                    return color.replace(/[^,]+(?=\))/, '0.9'); // Increase opacity on hover
                },
                hoverBorderColor: context => {
                    const color = context.dataset.borderColor[context.dataIndex];
                    return color;
                },
                hoverBorderWidth: 2
            }
        };
    } else if (chartType === 'line') {
        defaultOptions.scales = {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.03)',
                    drawBorder: false
                },
                border: {
                    dash: [4, 4]
                },
                ticks: {
                    font: {
                        size: 11,
                        family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                    },
                    color: 'rgba(0, 0, 0, 0.6)'
                }
            },
            x: {
                grid: {
                    display: false,
                    drawBorder: false
                },
                ticks: {
                    font: {
                        size: 11,
                        family: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif"
                    },
                    color: 'rgba(0, 0, 0, 0.6)'
                }
            }
        };

        // Enhanced line chart elements
        defaultOptions.elements = {
            line: {
                tension: 0.4, // Smoother curves
                borderWidth: 3,
                fill: true,
                // Add gradient fill
                backgroundColor: function(context) {
                    const chart = context.chart;
                    const {ctx, chartArea} = chart;
                    if (!chartArea) {
                        return null;
                    }
                    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
                    // Use the existing chartColorPalette from window object if already declared
                    const colorPalette = window.chartColorPalette || {
                        primary: [
                            'rgba(75, 192, 192, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(255, 99, 132, 1)'
                        ]
                    };
                    const colorKey = Math.floor(context.dataIndex % colorPalette.primary.length);
                    gradient.addColorStop(0, 'rgba(255, 255, 255, 0)');
                    gradient.addColorStop(1, colorPalette.primary[colorKey].replace(/[^,]+(?=\))/, '0.2'));
                    return gradient;
                }
            },
            point: {
                radius: 4,
                hoverRadius: 6,
                backgroundColor: 'white',
                borderWidth: 3
            }
        };

        // Format numbers in tooltips
        defaultOptions.plugins.tooltip.callbacks.label = function(context) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            // Format numbers with commas for thousands
            label += new Intl.NumberFormat().format(context.parsed.y);
            return label;
        };
    } else if (chartType === 'pie' || chartType === 'doughnut') {
        // Enhanced pie/doughnut chart options
        defaultOptions.cutout = chartType === 'doughnut' ? '70%' : '0';
        defaultOptions.radius = '90%';

        // Add hover effects
        defaultOptions.elements = {
            arc: {
                borderWidth: 2,
                borderColor: 'white',
                hoverBorderColor: 'white',
                hoverBorderWidth: 3,
                hoverOffset: 8
            }
        };

        // For pie/doughnut charts, customize tooltips to show percentages with better formatting
        defaultOptions.plugins.tooltip.callbacks.label = function(context) {
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            // Format numbers with commas for thousands
            const formattedValue = new Intl.NumberFormat().format(value);
            return `${label}: ${formattedValue} (${percentage}%)`;
        };
    }

    // For small screens, adjust the legend position
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    if (mediaQuery.matches) {
        defaultOptions.plugins.legend.position = 'bottom';
    }

    // Merge custom options with default options
    const chartOptions = customOptions ? { ...defaultOptions, ...customOptions } : defaultOptions;

    // Create the chart with enhanced options
    return new Chart(canvas, {
        type: chartType,
        data: {
            labels: chartLabels,
            datasets: [{
                label: canvas.closest('.card').querySelector('.card-header h5').textContent,
                data: chartData,
                backgroundColor: bgColors.slice(0, chartData.length),
                borderColor: borderColors.slice(0, chartData.length),
                borderWidth: 1,
                // Add additional styling for line charts
                ...(chartType === 'line' && {
                    tension: 0.3,
                    fill: true
                })
            }]
        },
        options: chartOptions
    });
}

// Export the function for use in other files
window.createEnhancedChart = createEnhancedChart;
