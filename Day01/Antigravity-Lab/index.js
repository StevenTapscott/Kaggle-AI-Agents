#!/usr/bin/env node

// Disable TLS verification to prevent CRYPT_E_NO_REVOCATION_CHECK errors on restricted networks
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import { spawn } from 'child_process';
import readline from 'readline';

const VALID_TOPICS = ['WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH'];

function printHelp() {
  console.log(`
\x1b[1;36mGoogle News CLI Tool\x1b[0m
Get the latest headlines from Google News right in your terminal.

\x1b[1;33mUsage:\x1b[0m
  node index.js [options]

\x1b[1;33mOptions:\x1b[0m
  -h, --help            Show this help message
  -s, --search <query>  Search for articles containing <query>
  -t, --topic <topic>   Get articles for a specific topic
                        Valid topics: \x1b[32m${VALID_TOPICS.join(', ')}\x1b[0m
  -l, --limit <number>  Limit the number of headlines displayed (default: 10)
  -d, --details         Show snippets/descriptions of the articles

\x1b[1;33mExamples:\x1b[0m
  node index.js
  node index.js --topic TECHNOLOGY --limit 5
  node index.js --search "artificial intelligence" --details
`);
}

function decodeEntities(str) {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&nbsp;/g, ' ');
}

function getTagContent(xml, tag) {
  const regex = new RegExp(`<${tag}(?:\\s+[^>]*)?>([\\s\\S]*?)<\\/${tag}>`, 'i');
  const match = xml.match(regex);
  if (!match) return '';
  let content = match[1].trim();
  
  if (content.startsWith('<![CDATA[') && content.endsWith(']]>')) {
    content = content.substring(9, content.length - 3);
  }
  
  return decodeEntities(content);
}

function cleanHtml(html) {
  if (!html) return '';
  let text = html.replace(/<[^>]*>/g, ' ');
  text = decodeEntities(text);
  return text.replace(/\s+/g, ' ').trim();
}

function formatRelativeDate(dateStr) {
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMin = Math.floor(diffMs / 60000);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffMin < 1) return 'just now';
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    return `${diffDay}d ago`;
  } catch {
    return dateStr;
  }
}

function openBrowser(url) {
  if (process.platform === 'win32') {
    spawn('cmd.exe', ['/c', 'start', '""', url], { detached: true, stdio: 'ignore' }).unref();
  } else if (process.platform === 'darwin') {
    spawn('open', [url], { detached: true, stdio: 'ignore' }).unref();
  } else {
    spawn('xdg-open', [url], { detached: true, stdio: 'ignore' }).unref();
  }
}

function startSpinner(text) {
  const chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  let i = 0;
  process.stdout.write(`\x1b[?25l`); // Hide cursor
  const interval = setInterval(() => {
    process.stdout.write(`\r\x1b[36m${chars[i]} \x1b[0m${text}`);
    i = (i + 1) % chars.length;
  }, 80);
  return { interval, text };
}

function stopSpinner(spinner, success, endText) {
  clearInterval(spinner.interval);
  process.stdout.write('\r\x1b[K'); // Clear line
  process.stdout.write(`\x1b[?25h`); // Show cursor
  if (success) {
    console.log(`\x1b[32m✔\x1b[0m ${endText || spinner.text}`);
  } else {
    console.log(`\x1b[31m✖\x1b[0m ${endText || spinner.text}`);
  }
}

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  let search = '';
  let topic = '';
  let limit = 10;
  let details = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--help' || arg === '-h') {
      printHelp();
      return;
    } else if (arg === '--search' || arg === '-s') {
      if (i + 1 >= args.length || args[i + 1].startsWith('-')) {
        console.error(`\x1b[31mError: Option '${arg}' requires an argument.\x1b[0m`);
        process.exitCode = 1;
        return;
      }
      search = args[++i];
    } else if (arg === '--topic' || arg === '-t') {
      if (i + 1 >= args.length || args[i + 1].startsWith('-')) {
        console.error(`\x1b[31mError: Option '${arg}' requires an argument.\x1b[0m`);
        process.exitCode = 1;
        return;
      }
      topic = args[++i].toUpperCase();
    } else if (arg === '--limit' || arg === '-l') {
      if (i + 1 >= args.length || args[i + 1].startsWith('-')) {
        console.error(`\x1b[31mError: Option '${arg}' requires an argument.\x1b[0m`);
        process.exitCode = 1;
        return;
      }
      const parsedLimit = parseInt(args[++i], 10);
      if (isNaN(parsedLimit) || parsedLimit <= 0) {
        console.error(`\x1b[31mError: Limit must be a positive integer.\x1b[0m`);
        process.exitCode = 1;
        return;
      }
      limit = parsedLimit;
    } else if (arg === '--details' || arg === '-d') {
      details = true;
    } else {
      console.error(`\x1b[31mError: Unknown option: ${arg}\x1b[0m`);
      printHelp();
      process.exitCode = 1;
      return;
    }
  }

  if (topic && !VALID_TOPICS.includes(topic)) {
    console.error(`\x1b[31mError: Invalid topic '${topic}'.\x1b[0m`);
    console.error(`Valid topics are: \x1b[32m${VALID_TOPICS.join(', ')}\x1b[0m`);
    process.exitCode = 1;
    return;
  }

  // Construct URL
  let url = 'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en';
  let titleContext = 'Top Headlines';
  if (search) {
    const queryEncoded = encodeURIComponent(search);
    url = `https://news.google.com/rss/search?q=${queryEncoded}&hl=en-US&gl=US&ceid=US:en`;
    titleContext = `Search Results: "${search}"`;
  } else if (topic) {
    url = `https://news.google.com/rss/headlines/section/topic/${topic}?hl=en-US&gl=US&ceid=US:en`;
    titleContext = `Topic: ${topic}`;
  }

  const spinner = startSpinner('Fetching latest news from Google...');
  let xml = '';
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    xml = await response.text();
    stopSpinner(spinner, true, 'News fetched successfully.');
  } catch (error) {
    stopSpinner(spinner, false, 'Failed to fetch news.');
    console.error(`\x1b[31mError: ${error.message}\x1b[0m`);
    process.exitCode = 1;
    return;
  }

  // Parse items
  const items = [];
  const itemMatches = xml.matchAll(/<item>([\s\S]*?)<\/item>/g);
  for (const match of itemMatches) {
    const itemXml = match[1];
    const title = getTagContent(itemXml, 'title');
    const link = getTagContent(itemXml, 'link');
    const pubDate = getTagContent(itemXml, 'pubDate');
    const description = getTagContent(itemXml, 'description');
    const source = getTagContent(itemXml, 'source');
    items.push({ title, link, pubDate, description, source });
  }

  const displayedItems = items.slice(0, limit);
  if (displayedItems.length === 0) {
    console.log('\n\x1b[33mNo articles found.\x1b[0m\n');
    return;
  }

  console.log(`\n\x1b[1;36m┌────────────────────────────────────────────────────────┐\x1b[0m`);
  console.log(`\x1b[1;36m│\x1b[0m  📰  \x1b[1;37mG O O G L E   N E W S   C L I\x1b[0m                    \x1b[1;36m│\x1b[0m`);
  console.log(`\x1b[1;36m└────────────────────────────────────────────────────────┘\x1b[0m`);
  console.log(`\x1b[35m● ${titleContext}\x1b[0m (showing ${displayedItems.length} of ${items.length} items)\n`);

  displayedItems.forEach((item, index) => {
    const num = String(index + 1).padStart(2, ' ');
    let cleanTitle = item.title;
    const sourceStr = item.source || 'Unknown';
    if (sourceStr && cleanTitle.endsWith(` - ${sourceStr}`)) {
      cleanTitle = cleanTitle.substring(0, cleanTitle.length - ` - ${sourceStr}`.length);
    }
    const timeFormatted = formatRelativeDate(item.pubDate);
    
    console.log(`\x1b[1;33m${num}.\x1b[0m \x1b[1;37m${cleanTitle}\x1b[0m`);
    console.log(`    \x1b[90mSource: \x1b[32m${sourceStr}\x1b[0m \x1b[90m| \x1b[36m${timeFormatted}\x1b[0m`);
    
    if (details && item.description) {
      const descClean = cleanHtml(item.description);
      const snippet = descClean.length > 180 ? descClean.substring(0, 177) + '...' : descClean;
      console.log(`    \x1b[2;37m${snippet}\x1b[0m`);
    }
    console.log();
  });

  // If not in a TTY terminal, do not prompt for user input and exit naturally
  if (!process.stdin.isTTY) {
    return;
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const prompt = () => {
    rl.question(`\x1b[1;34m👉 Enter article number to open (1-${displayedItems.length}), 'r' to refresh, or 'q' to quit: \x1b[0m`, (answer) => {
      const trimmed = answer.trim().toLowerCase();
      if (trimmed === 'q' || trimmed === 'quit' || trimmed === 'exit') {
        console.log('\n\x1b[33mGoodbye!\x1b[0m');
        rl.close();
        return;
      }
      
      if (trimmed === 'r' || trimmed === 'refresh') {
        rl.close();
        main();
        return;
      }
      
      const num = parseInt(trimmed, 10);
      if (!isNaN(num) && num >= 1 && num <= displayedItems.length) {
        const item = displayedItems[num - 1];
        console.log(`\n\x1b[32mOpening:\x1b[0m \x1b[1;37m${item.title}\x1b[0m`);
        console.log(`\x1b[90mURL: ${item.link}\x1b[0m\n`);
        openBrowser(item.link);
        prompt();
      } else {
        console.log('\x1b[31mInvalid input. Please enter a valid number, \'r\', or \'q\'.\x1b[0m');
        prompt();
      }
    });
  };

  prompt();
}

main().catch(err => {
  console.error('\x1b[31mFatal Error:\x1b[0m', err);
  process.exitCode = 1;
});
