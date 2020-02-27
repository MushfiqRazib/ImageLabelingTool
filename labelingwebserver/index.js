//include http, fs and url module
var http = require('http'),
    https = require('https'),
    fs = require('fs'),
    path = require('path'),
    url = require('url');
    
    // Files/Images path location defined in rootDir
    // rootDir = '/home/mushfiqrahman/dev/ProjectRoot';
    rootDir = '/home/labelapp/FZG-NAS/461_DatenBilderkennung';
    imageDir = '';


const hostname = '127.0.0.1';
//const hostname = '0.0.0.0';

//const hostname = '127.0.1.1'; // tumwfzg-lise.srv.mwn.de (127.0.1.1)
//const hostname = 'tumwfzg-lise.srv.mwn.de'; // tumwfzg-lise.srv.mwn.de (127.0.1.1)
const port = 9000;
const imageFileTypes = ['.png', '.jpeg', '.jpg', '.bmp', '.gif']

const options = {
    key: fs.readFileSync('/etc/ssl/private/nginx-selfsigned.key'),
    cert: fs.readFileSync('/etc/ssl/certs/nginx-selfsigned.crt')
  };
 
//create http server listening on port 9000
https.createServer(options, function (req, res) {
//http.createServer(function (req, res) {
    //use the url to parse the requested url and get the image name
    var query = url.parse(req.url,true).query;
        pic = query.image;
    //console.log(query)
    //console.log(pic)
    //console.log(url.parse(req.url))
    //console.log(`query: ${req.url}`);
    serverurl = 'https://' + hostname + ':' + port;
    if (typeof pic === 'undefined') {

        var imageFiles = getImageFilesFromDir(rootDir)
        //console.log(`calling getImageFilesFromDir: ${imageFiles}`);
        var imageLists = '<ul style="display: none;">';
        for (var i=0; i<imageFiles.length; i++) {
            var filename = path.basename(imageFiles[i]);
            //console.log(filename)
            var pathname = path.dirname(imageFiles[i]) + '/'
            imageDir = pathname
            //console.log(pathname)
            imageUrl = pathname + '?image=' + filename
            //console.log(`ImageUrl: ${imageUrl}`);
            imageLists += '<li><a href="' + pathname + '?image=' + filename + '">' + serverurl + imageUrl + '</li>';
        }
        imageLists += '</ul>';
        res.writeHead(200, {'Content-type':'text/html'});
        res.end(imageLists);
        //console.log(`html: ${imageLists}`);
            

        /*getImages(rootDir, function (err, files) {
            var imageLists = '<ul>';
            for (var i=0; i<files.length; i++) {
                //imageLists += '<li><a href="/?image=' + files[i] + '">' + files[i] + '</li>';
                imageUrl = rootDir + '?image=' + files[i]
                //console.log(`ImageUrl: ${imageUrl}`);

                //imageLists += '<li><a href="' + rootDir + '?image=' + files[i] + '">' + files[i] + '</li>';
                imageLists += '<li><a href="' + rootDir + '?image=' + files[i] + '">' + serverurl + imageUrl + '</li>';
            }
            imageLists += '</ul>';
            res.writeHead(200, {'Content-type':'text/html'});
            res.end(imageLists);
            console.log(`html: ${imageLists}`);
        });*/
        
    } else {
        //read the image using fs and send the image content back in the response
        fs.readFile(url.parse(req.url).pathname + pic, function (err, content) {
            if (err) {
                res.writeHead(400, {'Content-type':'text/html'})
                console.log(err);
                res.end("No such image");    
            } else {
                //specify the content type in the response will be an image
                res.writeHead(200, {'Content-type':'image/jpeg'});
                res.end(content);
            }
        });
    }
 
}).listen(port, () => {
    //console.log(`Server running at https://${hostname}:${port}/`);
    console.log(`Server running at ${port}/`);
  });

const fileTypes = {
    PNG: '.png',
    JPEG: '.jpeg',
    JPG: '.jpg',
    BMP: '.bmp', 
    GIF: '.gif'
}

//get the list of jpg files in the image dir
function getImages(rootDir, callback) {
    console.log(rootDir)
    //var fileType = '.jpeg',
    var files = [], i;
    console.log(imageFileTypes)
    fs.readdir(rootDir, function (err, list) {
        for(i=0; i<list.length; i++) {
            if(imageFileTypes.indexOf(path.extname(list[i])) != -1) {
            //if((path.extname(list[i]) === fileTypes.PNG) || 
               //(path.extname(list[i]) === fileTypes.JPEG) ||
               //(path.extname(list[i]) === fileTypes.JPG) ||
               //(path.extname(list[i]) === fileTypes.BMP) ||
               //(path.extname(list[i]) === fileTypes.GIF)) {
                
                   files.push(list[i]); //store the file name into the array files
            }
        }
        callback(err, files);
    });
}

// Return a list of files of the specified fileTypes in the provided dir, 
// with the file path relative to the given dir
// dir: path of the directory you want to search the files for
// fileTypes: array of file types you are search files, ex: ['.txt', '.jpg']
function getImageFilesFromDir(dir, callback) {
    var filesToReturn = [];
    function walkDir(currentPath) {
        var files = fs.readdirSync(currentPath);
        for (var i in files) {
            var curFile = path.join(currentPath, files[i]);      
            if (fs.statSync(curFile).isFile() && imageFileTypes.indexOf(path.extname(curFile)) != -1) {
                //console.log(dir)
                //console.log(curFile)
                //filesToReturn.push(curFile.replace(dir, ''));
                filesToReturn.push(curFile);
            } else if (fs.statSync(curFile).isDirectory()) {
                walkDir(curFile);
            }
        }
    };
    walkDir(dir);
    //console.log(filesToReturn)
    //console.log(`Returning from getImageFilesFromDir: ${filesToReturn}`);
    return filesToReturn; 
  }
