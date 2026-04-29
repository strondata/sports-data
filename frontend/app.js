const API_BASE_URL = 'http://localhost:8000/api/v1';
const TEAM_ID = '054efa67';

document.addEventListener('DOMContentLoaded', () => {
    fetchInsights();
    fetchMatches();
});

async function fetchInsights() {
    try {
        const response = await fetch(`${API_BASE_URL}/teams/${TEAM_ID}/insights`);
        const data = await response.json();

        const insightsList = document.getElementById('insights-list');
        insightsList.innerHTML = `
            <li class="flex justify-between border-b pb-1">
                <span class="text-gray-600">Avg xG (Last 5):</span>
                <span class="font-bold">${data.avg_xg_last_5_matches || 'N/A'}</span>
            </li>
            <li class="flex justify-between border-b pb-1">
                <span class="text-gray-600">Home Win Rate:</span>
                <span class="font-bold">${data.home_win_rate_pct}%</span>
            </li>
            <li class="flex justify-between">
                <span class="text-gray-600">Away Win Rate:</span>
                <span class="font-bold">${data.away_win_rate_pct}%</span>
            </li>
        `;
    } catch (error) {
        console.error('Error fetching insights:', error);
    }
}

async function fetchMatches() {
    try {
        const response = await fetch(`${API_BASE_URL}/teams/${TEAM_ID}/matches`);
        const matches = await response.json();

        // Reverse array because API returns desc (newest first),
        // we might want chronological for charts or keep desc for table.
        // Let's use it directly for table (descending), and reverse for charts.

        populateTable(matches);
        findNextMatch(matches);

        // For chart, we want chronological order of played matches
        const playedMatches = matches.filter(m => m.result !== null).reverse();
        renderChart(playedMatches);

    } catch (error) {
        console.error('Error fetching matches:', error);
    }
}

function populateTable(matches) {
    const tbody = document.getElementById('matches-table-body');
    tbody.innerHTML = '';

    matches.forEach(m => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-gray-50";

        const isUpcoming = m.result === null;
        const resClass = m.result === 'W' ? 'text-green-600 font-bold' :
                         m.result === 'L' ? 'text-red-600 font-bold' :
                         m.result === 'D' ? 'text-yellow-600 font-bold' : '';

        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">${m.match_date}</td>
            <td class="px-6 py-4 whitespace-nowrap">${m.competition}</td>
            <td class="px-6 py-4 whitespace-nowrap">${m.venue}</td>
            <td class="px-6 py-4 whitespace-nowrap">${m.opponent_name}</td>
            <td class="px-6 py-4 whitespace-nowrap ${resClass}">${m.result || '-'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right">${isUpcoming ? '-' : m.goals_for}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right">${isUpcoming ? '-' : m.goals_against}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right">${m.xg_for || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function findNextMatch(matches) {
    // Matches are sorted DESC by date.
    // The next match is the one closest to today in the future,
    // or the one with no result yet.
    const upcoming = matches.filter(m => m.result === null);

    // Reverse to get the earliest upcoming match
    upcoming.reverse();

    const nextMatchContainer = document.getElementById('next-match-details');
    if (upcoming.length > 0) {
        const next = upcoming[0];
        nextMatchContainer.innerHTML = `
            <div class="text-2xl">${next.opponent_name}</div>
            <div class="text-sm mt-1 opacity-80">${next.match_date} | ${next.venue} | ${next.competition}</div>
        `;
    } else {
        nextMatchContainer.innerHTML = 'No upcoming matches found.';
    }
}

function renderChart(matches) {
    const ctx = document.getElementById('gfXgChart').getContext('2d');

    const labels = matches.map(m => m.match_date);
    const gfData = matches.map(m => m.goals_for);
    const xgData = matches.map(m => m.xg_for);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Goals For (GF)',
                    data: gfData,
                    borderColor: 'rgba(59, 130, 246, 1)', // blue-500
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Expected Goals (xG)',
                    data: xgData,
                    borderColor: 'rgba(16, 185, 129, 1)', // green-500
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Goals'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}
