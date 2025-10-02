import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  GetCloudFrontOriginAccessIdentityConfigRequest,
  GetCloudFrontOriginAccessIdentityConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetCloudFrontOriginAccessIdentityConfigCommandInput
  extends GetCloudFrontOriginAccessIdentityConfigRequest {}
export interface GetCloudFrontOriginAccessIdentityConfigCommandOutput
  extends GetCloudFrontOriginAccessIdentityConfigResult,
    __MetadataBearer {}
export declare class GetCloudFrontOriginAccessIdentityConfigCommand extends $Command<
  GetCloudFrontOriginAccessIdentityConfigCommandInput,
  GetCloudFrontOriginAccessIdentityConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetCloudFrontOriginAccessIdentityConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetCloudFrontOriginAccessIdentityConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetCloudFrontOriginAccessIdentityConfigCommandInput,
    GetCloudFrontOriginAccessIdentityConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
