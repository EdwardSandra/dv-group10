<script>
// @ts-nocheck

	import { onMount } from 'svelte';
	import Papa from 'papaparse';
	import * as d3 from 'd3';

	/**
	 * @type {any[]}
	 */
	let orders = [];
	/**
	 * @type {any[]}
	 */
	let data;
	/**
	 * @type {any[]}
	 */
	let regions = [];


	/**
	 * @type {any[]}
	 */
	let avgDeliveryTimeAndNbOrdersPerRegion = [];

	const colors = [
		[0, 0, 255], // Blue
		[173, 216, 230], // Light Blue
		[0, 216, 0], // Green
		[255, 255, 0], // Yellow
		[255, 165, 0], // Orange
		[255, 0, 0] // Red
	];

	/**
	 * @type {any[]}
	 */
	let interpolateColors = [];
	/**
	 * @type {any[]}
	 */
	let gradLabels = [];

	/**
	 * @type {string | any[]}
	 */
	let sizeLabels = [];

	/**
	 * @type {number}
	 */
	let maxNbOrders;

	/**
	 * @type {number}
	 */
	let minNbOrders;

	let maxRadius = 30;

	// Function to calculate color gradient between red and blue
	/**
	 * @param {number} value
	 * @param {number} min
	 * @param {number} max
	 */
	function interpolateColor(value, min, max) {
		let r, g, b;

		if (!value || !min || !max)
			return '#000000';
		if (max - min === 0) {
			[r, g, b] = [255, 0, 0];
			return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
		}
			
		// Calculate normalized value between 0 and 1
		const normalizedValue = (value - min) / (max - min);

		// Calculate the index for color interpolation
		const index = Math.floor(normalizedValue * (colors.length - 1));

		if (index !== colors.length - 1) {
			// Interpolate color between adjacent colors
			const [r1, g1, b1] = colors[index];
			const [r2, g2, b2] = colors[index + 1];
			const ratio = (normalizedValue - index / (colors.length - 1)) * (colors.length - 1);
			r = Math.floor(r1 + (r2 - r1) * ratio);
			g = Math.floor(g1 + (g2 - g1) * ratio);
			b = Math.floor(b1 + (b2 - b1) * ratio);
		} else {
			[r, g, b] = colors[index];
		}

		// Return color in hexadecimal format
		return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
	}
	/**
	 * @type {number}
	 */
	let minAvgDeliveryTime;
	/**
	 * @type {number}
	 */
	let maxAvgDeliveryTime;

	/**
	 * @type {number}
	 */
	let minAverageDeliveryTimeSlider;
	let maxAverageDeliveryTimeSlider;
	/**
	 * @type {number}
	 */
	let minNbOrdersSlider;
	/**
	 * @type {number}
	 */
	let maxNbOrdersSlider;

	let constMinAvgDeliveryTime = 0;
	let constMaxAvgDeliveryTime = 120;
	let constMinNbOrders = 0;
	let constMaxNbOrders = 100000000;

	minAverageDeliveryTimeSlider = 0;
	maxAverageDeliveryTimeSlider = 100000000;
	minNbOrdersSlider = 0;
	maxNbOrdersSlider = 100000000;

	const diagonalLinesOffset = 75;

	const months = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December'
	];

	/**
	 * @type {number}
	 */
	let maxDeliveryTimePerMonth;

	const load = async () => {
		const response = await fetch('src/data/orders.csv');
		const csvText = await response.text();
		orders = Papa.parse(csvText, { header: true }).data;

		const reponseRegions = await fetch('src/data/regions.csv');
		const csvTextRegions = await reponseRegions.text();
		regions = Papa.parse(csvTextRegions, { header: true }).data;

		orders = orders.map((item) => {
			return {
				...item,
				'Delivery Time': calculateDeliveryTime(item['OrderDate'], item['DeliveryDate']),
				month: new Date(item['OrderDate']).getMonth() + 1
			};
		});

		avgDeliveryTimeAndNbOrdersPerRegion = orders.reduce((acc, item) => {
			const area = findArea(item['Territory'], regions);
			const territory = item['Territory'];
			if (!acc[territory]) {
				acc[territory] = {
					'Total Delivery Time': 0,
					'Total Orders': 0,
					'Total Delivery Time per Month': {
						1: 0,
						2: 0,
						3: 0,
						4: 0,
						5: 0,
						6: 0,
						7: 0,
						8: 0,
						9: 0,
						10: 0,
						11: 0,
						12: 0
					},
					'Total Orders per Month': {
						1: 0,
						2: 0,
						3: 0,
						4: 0,
						5: 0,
						6: 0,
						7: 0,
						8: 0,
						9: 0,
						10: 0,
						11: 0,
						12: 0
					}
				};
			}
			acc[territory]['Total Delivery Time'] += item['Delivery Time'];
			acc[territory]['Total Delivery Time per Month'][item['month']] += item['Delivery Time'];
			acc[territory]['Total Orders'] += 1;
			acc[territory]['Total Orders per Month'][item['month']] += 1;
			acc[territory]['Area'] = area;
			return acc;
		}, {});


		avgDeliveryTimeAndNbOrdersPerRegion = Object.keys(avgDeliveryTimeAndNbOrdersPerRegion).map(
			(key) => {
				return {
					Territory: key,
					// @ts-ignore
					Area: avgDeliveryTimeAndNbOrdersPerRegion[key]['Area'],
					// @ts-ignore
					'Average Delivery Time':
						Math.round(
							// @ts-ignore
							// @ts-ignore
							(avgDeliveryTimeAndNbOrdersPerRegion[key]['Total Delivery Time'] /
								// @ts-ignore
								avgDeliveryTimeAndNbOrdersPerRegion[key]['Total Orders']) *
								100
						) / 100,
					// @ts-ignore
					'Total Orders': avgDeliveryTimeAndNbOrdersPerRegion[key]['Total Orders'],
					'Total Delivery Time per Month': Object.keys(
						// @ts-ignore
						avgDeliveryTimeAndNbOrdersPerRegion[key]['Total Delivery Time per Month']
					).map((month) => {
						return {
							month: months[Number(month) - 1],
							avgDeliveryTime:
								Math.round(
									// @ts-ignore
									(avgDeliveryTimeAndNbOrdersPerRegion[key]['Total Delivery Time per Month'][
										month
									// @ts-ignore
									] /
										// @ts-ignore
										avgDeliveryTimeAndNbOrdersPerRegion[key]['Total Orders per Month'][month]) *
										100
								) / 100
						};
					})
				};
			}
		);
		avgDeliveryTimeAndNbOrdersPerRegion = avgDeliveryTimeAndNbOrdersPerRegion.filter(
			(item) => item['Area'] !== undefined
		);

		maxNbOrders = Math.max(
			...avgDeliveryTimeAndNbOrdersPerRegion.map((item) => item['Total Orders'])
		);
		minNbOrders = Math.min(
			...avgDeliveryTimeAndNbOrdersPerRegion.map((item) => item['Total Orders'])
		);
		constMinNbOrders = minNbOrders;
		constMaxNbOrders = maxNbOrders;

		avgDeliveryTimeAndNbOrdersPerRegion = avgDeliveryTimeAndNbOrdersPerRegion.map((item) => {
			return {
				...item,
				Radius: (item['Total Orders'] / maxNbOrders) * maxRadius
			};
		});

		const totalArea = avgDeliveryTimeAndNbOrdersPerRegion.reduce((acc, item) => {
			return acc + item['Radius'] ** 2 * Math.PI;
		}, 0);

		const radiusStep = 1;
		const angleStep = 0.01;
		/**
		 * @type {{ x: number; y: number; radius: any; }[]}
		 */
		const occupiedArea = [];
		// add small circles to diagonals
		const diagonalRadius = 2;
		for (let a = Math.PI / 4; a < 2 * Math.PI; a += Math.PI / 2) {
			for (
				let i = diagonalLinesOffset / diagonalRadius;
				i < 500 / diagonalRadius;
				i = i + diagonalRadius
			) {
				const x = i * diagonalRadius * Math.cos(a);
				const y = i * diagonalRadius * Math.sin(a);
				occupiedArea.push({
					x,
					y,
					radius: diagonalRadius
				});
			}
		}

		const order = ['Underdark', 'North', 'South', 'East', 'West'];
		avgDeliveryTimeAndNbOrdersPerRegion = avgDeliveryTimeAndNbOrdersPerRegion.sort((a, b) => {
			return order.indexOf(a['Area']) - order.indexOf(b['Area']);
		});
		avgDeliveryTimeAndNbOrdersPerRegion = avgDeliveryTimeAndNbOrdersPerRegion.map((item) => {
			// avoid overlapping
			let angle = 0;
			let radius = 0;
			let isAllowed = false;
			while (true) {
				isAllowed = false;
				switch (item['Area']) {
					case 'South':
						if (
							angle >= Math.PI / 4 &&
							angle <= (3 * Math.PI) / 4 &&
							radius >= diagonalLinesOffset
						) {
							isAllowed = true;
						}
						break;
					case 'North':
						if (
							angle >= (5 * Math.PI) / 4 &&
							angle <= (7 * Math.PI) / 4 &&
							radius >= diagonalLinesOffset
						) {
							isAllowed = true;
						}
						break;
					case 'East':
						if (
							((angle >= 0 && angle <= Math.PI / 4) ||
								(angle >= (7 * Math.PI) / 4 && angle <= 2 * Math.PI)) &&
							radius >= diagonalLinesOffset
						) {
							isAllowed = true;
						}
						break;
					case 'West':
						if (
							angle >= (3 * Math.PI) / 4 &&
							angle <= (5 * Math.PI) / 4 &&
							radius >= diagonalLinesOffset
						) {
							isAllowed = true;
						}
						break;
					case 'Underdark':
						isAllowed = true;
						break;
				}

				if (isAllowed) {
					const x = radius * Math.cos(angle);
					const y = radius * Math.sin(angle);
					const circle = {
						x,
						y,
						radius: item['Radius']
					};
					const overlapping = occupiedArea.some((occupiedCircle) => {
						const distance = Math.sqrt(
							(occupiedCircle.x - circle.x) ** 2 + (occupiedCircle.y - circle.y) ** 2
						);
						return distance < occupiedCircle.radius + circle.radius;
					});
					if (!overlapping) {
						occupiedArea.push(circle);
						return {
							...item,
							x,
							y
						};
					}
				}

				angle += angleStep;
				if (angle >= 2 * Math.PI) {
					angle = 0;
					radius += radiusStep;
				}
			}
		});

	};

	/**
	 * @param {any} territory
	 * @param {any[]} regs
	 */
	function findArea(territory, regs) {
		const region = regs.find((region) => region['Territory'] === territory);
		return region?.Area;
	}

	/**
	 * @param {string | number | Date} orderDate
	 * @param {string | number | Date} deliveryDate
	 */
	function calculateDeliveryTime(orderDate, deliveryDate) {
		const orderDateTime = new Date(orderDate);
		const deliveryDateTime = new Date(deliveryDate);
		// @ts-ignore
		const timeDifference = deliveryDateTime - orderDateTime;
		const daysDifference = Math.ceil(timeDifference / (1000 * 3600 * 24));
		return daysDifference;
	}

	/**
	 * @param {number} startValue
	 * @param {number} stopValue
	 * @param {number} cardinality
	 */
	function makeArr(stopValue, startValue, cardinality) {
		var arr = [];
		var step = (stopValue - startValue) / (cardinality - 1);
		for (var i = 0; i < cardinality; i++) {
			arr.push(startValue + step * i);
		}
		return arr;
	}

	/**
	 * @param {number} i
	 * @param {number} margin
	 * @returns {number}
	 */
	function getYCoordinateSizeLegend(i, margin) {
		if (i - 1 < 0) {
			return (maxRadius * sizeLabels[i]) / maxNbOrders;
		}
		return (
			getYCoordinateSizeLegend(i - 1, margin) +
			(maxRadius * sizeLabels[i - 1]) / maxNbOrders +
			(maxRadius * sizeLabels[i]) / maxNbOrders +
			margin
		);
	}

	/**
	 * @type {{ [x: string]: any; Territory: any; } | undefined}
	 */
	export let selected_datapoint = undefined;
	/**
	 * @type {number}
	 */
	let mouse_x;
	/**
	 * @type {number}
	 */
	let mouse_y;
	const setMousePosition = function (
		/** @type {MouseEvent & { currentTarget: EventTarget & SVGCircleElement; }} */ event
	) {
		mouse_x = event.clientX;
		mouse_y = event.clientY;
	};

	const widthHistogram = 300;
	const heightHistogram = Math.round(widthHistogram * 0.75);

	let xHistogram;

	/**
	 * @type {any[]}
	 */
	let dataHistogram;
	dataHistogram = [
		{ month: 'January', avgDeliveryTime: 10 },
		{ month: 'February', avgDeliveryTime: 20 },
		{ month: 'March', avgDeliveryTime: 30 },
		{ month: 'April', avgDeliveryTime: 40 },
		{ month: 'May', avgDeliveryTime: 50 },
		{ month: 'June', avgDeliveryTime: 60 },
		{ month: 'July', avgDeliveryTime: 70 },
		{ month: 'August', avgDeliveryTime: 80 },
		{ month: 'September', avgDeliveryTime: 90 },
		{ month: 'October', avgDeliveryTime: 100 },
		{ month: 'November', avgDeliveryTime: 110 },
		{ month: 'December', avgDeliveryTime: 120 }
	];

	$: xHistogram = d3
		.scaleBand()
		.domain(dataHistogram.map((d) => d.month))
		.range([0, widthHistogram])
		.padding(0.1);

	/**
	 * @type {{ (arg0: any): number; (arg0: any): number; ticks: any; }}
	 */
	let yHistogram;

	$: maxDeliveryTimePerMonth = Math.max(
			...data.map((item) =>
				Math.max(...item['Total Delivery Time per Month'].map((/** @type {{ avgDeliveryTime: any; }} */ month) => month.avgDeliveryTime))
			)
		);
	
	let avgDeliveryTimes;
	$: avgDeliveryTimes = data.map(
			(dp) => dp['Average Delivery Time']
		);
	$: minAvgDeliveryTime = Math.min(...avgDeliveryTimes);
	$: maxAvgDeliveryTime = Math.max(...avgDeliveryTimes);

	$: interpolateColors = makeArr(minAvgDeliveryTime, maxAvgDeliveryTime, 200).map((value) =>
		interpolateColor(value, minAvgDeliveryTime, maxAvgDeliveryTime)
	);

	$: gradLabels = makeArr(minAvgDeliveryTime, maxAvgDeliveryTime, 10).map(
		(value) => Math.round(value * 100) / 100
	);

	$: sizeLabels = makeArr(maxNbOrders, minNbOrders, 5).map((value) => Math.round(value * 100) / 100);

	$: yHistogram = d3
	.scaleLinear()
	.domain([
		0,
		maxDeliveryTimePerMonth
	])
	.nice()
	.range([heightHistogram, 0]);

	$: data = avgDeliveryTimeAndNbOrdersPerRegion.length > 0 ? avgDeliveryTimeAndNbOrdersPerRegion.filter(
		(item) =>
			item['Total Orders'] >= minNbOrdersSlider &&
			item['Total Orders'] <= maxNbOrdersSlider &&
			item['Average Delivery Time'] >= minAverageDeliveryTimeSlider &&
			item['Average Delivery Time'] <= maxAverageDeliveryTimeSlider
	) : [];

	onMount(async () => {
		await load();

		minAverageDeliveryTimeSlider = minAvgDeliveryTime;
		maxAverageDeliveryTimeSlider = maxAvgDeliveryTime;
		constMinAvgDeliveryTime = minAvgDeliveryTime;
		constMaxAvgDeliveryTime = maxAvgDeliveryTime;
		minNbOrdersSlider = minNbOrders;
		maxNbOrdersSlider = maxNbOrders;
		console.log('avgDeliveryTimeAndNbOrdersPerRegion', avgDeliveryTimeAndNbOrdersPerRegion);
	});
</script>

{#if data}

	<svg width="1000" height="800">
		<text x="400" y="25" text-anchor="middle" font-size="24" fill="black"
			>Order amount & average delivery time per territory</text
		>
		<text x="400" y="50" text-anchor="middle" font-size="16" fill="black">North</text>
		<text x="400" y="775" text-anchor="middle" font-size="16" fill="black">South</text>
		<text
			x="50"
			y="400"
			text-anchor="middle"
			font-size="16"
			fill="black"
			transform="rotate(-90 50 400)">West</text
		>
		<text
			x="750"
			y="400"
			text-anchor="middle"
			font-size="16"
			fill="black"
			transform="rotate(90 750 400)">East</text
		>
		<text x="400" y="370" text-anchor="middle" font-size="12" fill="black">Underdark</text>

		<!-- Diagonal from top-left to bottom-right -->
		<line
			x1="150"
			y1="150"
			x2={400 - (diagonalLinesOffset * 2) / 3}
			y2={400 - (diagonalLinesOffset * 2) / 3}
			stroke="grey"
			stroke-width="2"
		/>
		<line
			x1={400 + (diagonalLinesOffset * 2) / 3}
			y1={400 + (diagonalLinesOffset * 2) / 3}
			x2="650"
			y2="650"
			stroke="grey"
			stroke-width="2"
		/>

		<!-- Diagonal from top-right to bottom-left -->
		<line
			x1="650"
			y1="150"
			x2={400 + (diagonalLinesOffset * 2) / 3}
			y2={400 - (diagonalLinesOffset * 2) / 3}
			stroke="grey"
			stroke-width="2"
		/>
		<line
			x1={400 - (diagonalLinesOffset * 2) / 3}
			y1={400 + (diagonalLinesOffset * 2) / 3}
			x2="150"
			y2="650"
			stroke="grey"
			stroke-width="2"
		/>

		<!-- gradient -->
		{#each interpolateColors as ic, i (i)}
			<line
				y1={100 + i * 3}
				x1="900"
				y2={100 + (i + 1) * 3}
				x2="900"
				stroke={ic}
				stroke-width="10"
			/>
		{/each}
		{#each gradLabels as label, i (i)}
			<text
				x="910"
				y={115 + i * (580 / (gradLabels.length - 1))}
				text-anchor="start"
				font-size="12"
				fill="black">{label}</text
			>
		{/each}
		<text x="900" y={90} text-anchor="middle" font-size="12" fill="black"
			>average delivery time (days)</text
		>

		<!-- Circle nb orders -->
		<!-- <circle cx="50" cy="100" r="30" fill="none" stroke="black" stroke-width="1" />

		<line x1="20" y1="100" x2="65" y2="100" stroke="black" stroke-width="1" />

		<polygon points="20,100 35,95 35,105" fill="black" />

		<polygon points="80,100 65,95 65,105" fill="black" />

		<text x="50" y="90" text-anchor="middle" font-size="12" fill="black">#orders</text> -->

		<text x="750" y={90} text-anchor="middle" font-size="12" fill="black">order amount</text>
		{#each sizeLabels as sl, i (i)}
			<circle
				cx="750"
				cy={110 + getYCoordinateSizeLegend(i, 20)}
				r={(maxRadius * sl) / maxNbOrders}
				fill="none"
				stroke="black"
				stroke-width="1"
			/>
			<text
				x="790"
				y={113 + getYCoordinateSizeLegend(i, 20)}
				text-anchor="start"
				font-size="12"
				fill="black">{sl}</text
			>
		{/each}

		{#each data as dp}
			<circle
				cx={dp.x + 400}
				cy={dp.y + 400}
				r={dp['Radius']}
				class={dp['Area'] +
					(selected_datapoint && dp.Territory == selected_datapoint.Territory ? ' selected' : '')}
				role="button"
				tabindex="0"
				on:mouseover={function (event) {
					selected_datapoint = dp;
					setMousePosition(event);
					dataHistogram = dp['Total Delivery Time per Month'];
				}}
				on:focus={function (e) {}}
				on:mouseout={function () {
					selected_datapoint = undefined;
				}}
				on:blur={function () {
					selected_datapoint = undefined;
				}}
				style={'fill: ' +
					interpolateColor(dp['Average Delivery Time'], minAvgDeliveryTime, maxAvgDeliveryTime)}
			/>
		{/each}
	</svg>
	<div style="font-size: 12px; display: flex; align-items: center; justify-content: center;">
		<div style="display: flex; align-items: center; flex-direction: column; text-align: center;">
			<span style="margin-right: 10px;">Minimum #orders: {minNbOrdersSlider}</span>
			<input type="range" min={constMinNbOrders} max={maxNbOrdersSlider} step="1" class="slider" style="max-width: 100px;" bind:value={minNbOrdersSlider} />
		</div>
		<div style="display: flex; align-items: center; flex-direction: column; text-align: center;">
			<span style="margin-right: 10px; margin-left: 20px;">Maximum #orders: {maxNbOrdersSlider}</span>
			<input type="range" min={minNbOrdersSlider} max={constMaxNbOrders} step="1" class="slider" style="max-width: 100px;" bind:value={maxNbOrdersSlider} />
		</div>
		<div style="display: flex; align-items: center; flex-direction: column; text-align: center;">
			<span style="margin-right: 10px; margin-left: 20px;">Minimum average delivery time: {minAverageDeliveryTimeSlider}</span>
			<input type="range" min={constMinAvgDeliveryTime} max={maxAverageDeliveryTimeSlider} step="0.01" class="slider" style="max-width: 100px;" bind:value={minAverageDeliveryTimeSlider} />
		</div>
		<div style="display: flex; align-items: center; flex-direction: column; text-align: center;">
			<span style="margin-right: 10px; margin-left: 20px;">Maximum average delivery time: {maxAverageDeliveryTimeSlider}</span>
			<input type="range" min={minAverageDeliveryTimeSlider} max={constMaxAvgDeliveryTime} step="0.01" class="slider" style="max-width: 100px;" bind:value={maxAverageDeliveryTimeSlider} />
		</div>
	</div>

	{#if selected_datapoint != undefined}
		<div id="tooltip" style="left: {mouse_x + 10}px; top: {mouse_y - 10}px; font-size: 12px;">
			Territory: {selected_datapoint.Territory} ({selected_datapoint.Area})<br />
			Order amount: {selected_datapoint['Total Orders']} <br />
			Average delivery time: {selected_datapoint['Average Delivery Time']} days <br />

			<svg width="350" height={heightHistogram + 100}>
				<text x="180" y={20} text-anchor="middle" font-size="12" fill="black">Average delivery time per month</text>
				{#each dataHistogram as item}
					<rect
						class="bar"
						x={xHistogram(item.month) + 30}
						y={yHistogram(item.avgDeliveryTime) + 50}
						width={xHistogram.bandwidth()}
						height={heightHistogram - yHistogram(item.avgDeliveryTime)}
						fill="steelblue"
					/>
				{/each}
				<g class="x-axis">
					{#each dataHistogram as item}
						<text
							transform={`translate(${xHistogram(item.month) + xHistogram.bandwidth() / 2 + 30},${heightHistogram + 10 + 50}) rotate(-45)`}
							style="text-anchor: end;"
						>
							{item.month}
						</text>
					{/each}
				</g>

				<g class="y-axis">
					<g>
						{#each yHistogram.ticks() as tick}
							<line
								x1="30"
								y1={yHistogram(tick) + 50}
								x2={widthHistogram + 30}
								y2={yHistogram(tick) + 50}
								stroke="#ccc"
								style="opacity: 0.3;"
							/>
							<text x="25" y={yHistogram(tick) + 50} dy="0.35em" text-anchor="end">{tick}</text>
						{/each}
						<text x="17" y="35" text-anchor="middle">#days</text>
					</g>
				</g>
			</svg>
		</div>
	{/if}
{:else}
	<p>Loading...</p>
{/if}

<style>
	circle {
		fill-opacity: 0.5;
	}
	circle.selected {
		fill-opacity: 1;
	}
	#tooltip {
		position: fixed;
		background-color: white;
		padding: 3px;
		border: solid 1px;
	}
</style>
