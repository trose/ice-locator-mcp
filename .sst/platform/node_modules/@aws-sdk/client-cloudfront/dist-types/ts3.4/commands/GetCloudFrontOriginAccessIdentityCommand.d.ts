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
  GetCloudFrontOriginAccessIdentityRequest,
  GetCloudFrontOriginAccessIdentityResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetCloudFrontOriginAccessIdentityCommandInput
  extends GetCloudFrontOriginAccessIdentityRequest {}
export interface GetCloudFrontOriginAccessIdentityCommandOutput
  extends GetCloudFrontOriginAccessIdentityResult,
    __MetadataBearer {}
export declare class GetCloudFrontOriginAccessIdentityCommand extends $Command<
  GetCloudFrontOriginAccessIdentityCommandInput,
  GetCloudFrontOriginAccessIdentityCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetCloudFrontOriginAccessIdentityCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetCloudFrontOriginAccessIdentityCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetCloudFrontOriginAccessIdentityCommandInput,
    GetCloudFrontOriginAccessIdentityCommandOutput
  >;
  private serialize;
  private deserialize;
}
