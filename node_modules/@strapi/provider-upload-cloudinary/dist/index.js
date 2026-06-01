'use strict';

var cloudinary = require('cloudinary');
var intoStream = require('into-stream');
var utils = require('@strapi/utils');

function _interopNamespaceDefault(e) {
  var n = Object.create(null);
  if (e) {
    Object.keys(e).forEach(function (k) {
      if (k !== 'default') {
        var d = Object.getOwnPropertyDescriptor(e, k);
        Object.defineProperty(n, k, d.get ? d : {
          enumerable: true,
          get: function () { return e[k]; }
        });
      }
    });
  }
  n.default = e;
  return Object.freeze(n);
}

var utils__namespace = /*#__PURE__*/_interopNamespaceDefault(utils);

var index = {
    init (options) {
        cloudinary.v2.config(options);
        const upload = (file, customConfig = {})=>{
            return new Promise((resolve, reject)=>{
                const config = {
                    resource_type: 'auto',
                    public_id: file.hash
                };
                if (file.ext) {
                    config.filename = `${file.hash}${file.ext}`;
                }
                if (file.path) {
                    config.folder = file.path;
                }
                // For files smaller than 99 MB use regular upload as it tends to be faster
                // and fallback to chunked upload for larger files as that's required by Cloudinary.
                // https://support.cloudinary.com/hc/en-us/community/posts/360009586100-Upload-movie-video-with-large-size?page=1#community_comment_360002140099
                // The Cloudinary's max limit for regular upload is actually 100 MB but add some headroom
                // for size counting shenanigans. (Strapi provides the size in kilobytes rounded to two decimal places here).
                const uploadMethod = file.size && file.size < 1000 * 99 ? cloudinary.v2.uploader.upload_stream : cloudinary.v2.uploader.upload_chunked_stream;
                const uploadStream = uploadMethod({
                    ...config,
                    ...customConfig
                }, (err, image)=>{
                    if (err) {
                        if (err.message.includes('File size too large')) {
                            reject(new utils__namespace.errors.PayloadTooLargeError());
                        } else {
                            reject(new Error(`Error uploading to cloudinary: ${err.message}`));
                        }
                        return;
                    }
                    if (!image) {
                        return;
                    }
                    if (image.resource_type === 'video') {
                        file.previewUrl = cloudinary.v2.url(`${image.public_id}.gif`, {
                            video_sampling: 6,
                            delay: 200,
                            width: 250,
                            crop: 'scale',
                            resource_type: 'video'
                        });
                    }
                    file.url = image.secure_url;
                    file.provider_metadata = {
                        public_id: image.public_id,
                        resource_type: image.resource_type
                    };
                    resolve();
                });
                if (file.stream) {
                    file.stream.pipe(uploadStream);
                } else if (file.buffer) {
                    intoStream(file.buffer).pipe(uploadStream);
                } else {
                    throw new Error('Missing file stream or buffer');
                }
            });
        };
        return {
            uploadStream (file, customConfig = {}) {
                return upload(file, customConfig);
            },
            upload (file, customConfig = {}) {
                return upload(file, customConfig);
            },
            async delete (file, customConfig = {}) {
                try {
                    const { resource_type: resourceType, public_id: publicId } = file.provider_metadata ?? {};
                    const deleteConfig = {
                        resource_type: resourceType || 'image',
                        invalidate: true,
                        ...customConfig
                    };
                    const response = await cloudinary.v2.uploader.destroy(`${publicId}`, deleteConfig);
                    if (response.result !== 'ok' && response.result !== 'not found') {
                        throw new Error(response.result);
                    }
                } catch (error) {
                    if (error instanceof Error) {
                        throw new Error(`Error deleting on cloudinary: ${error.message}`);
                    }
                    throw error;
                }
            }
        };
    }
};

module.exports = index;
//# sourceMappingURL=index.js.map
