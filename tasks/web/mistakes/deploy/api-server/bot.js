const puppeteer = require('puppeteer')
const sleep = async ms => new Promise(resolve => setTimeout(resolve, ms))

let browser = null

const visit = async url => {
	let context = null
	try {
		if (!browser) {
			const args = ['--js-flags=--jitless,--no-expose-wasm', '--disable-gpu', '--disable-dev-shm-usage', '--no-sandbox']
			browser = await puppeteer.launch({
				headless: 'new',
				args
			})
		}
		
		context = await browser.createIncognitoBrowserContext()
		const page1 = await context.newPage()
		await page1.goto(process.env.STATIC_BASE)
		const FLAG = process.env.FLAG;
        await page1.evaluate(FLAG => {
            localStorage.setItem('flag', FLAG);
        },FLAG);	  
	  	console.log(`Go to ${url}`)
		await page1.goto(url)
		await sleep(5000)
		await page1.close()
		await context.close()
		context = null
	} catch (e) {
		console.log(e)
	} finally {
		if (context) await context.close()
	}
}
module.exports = visit;