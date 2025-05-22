{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "target": "es2017",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true
  },
  "exclude": ["node_modules", "dist"]
}







root@srv791876:~/neurapay-backend# npm cache clean --force
npm WARN using --force Recommended protections disabled.
root@srv791876:~/neurapay-backend# npm install
npm ERR! code E404
npm ERR! 404 Not Found - GET https://registry.npmjs.org/@nestjs%2fredis - Not found
npm ERR! 404 
npm ERR! 404  '@nestjs/redis@^9.0.0' is not in this registry.
npm ERR! 404 
npm ERR! 404 Note that you can also install from a
npm ERR! 404 tarball, folder, http url, or git url.

npm ERR! A complete log of this run can be found in:
npm ERR!     /root/.npm/_logs/2025-05-22T00_01_28_219Z-debug-0.log
